"""Точка входа GUI-эмулятора оболочки с поддержкой Этапа 4."""

import getpass
import socket
import sys

import customtkinter as ctk

from .config import Config, debug_dump, parse_args
from .shell import ShellState, execute, is_exit, parse_input, run_script
from .vfs_io import VFSError, load_vfs_from_csv

WINDOW_TITLE_TEMPLATE = "Shell Emulator - [{user}@{host}]"
WINDOW_SIZE = "900x600"
FONT_FAMILY = "JetBrains Mono"
FONT_SIZE = 14
PADDING = 10
SCRIPT_REPLAY_DELAY_MS = 400


def build_title() -> str:
    """Формирует заголовок окна из реальных данных ОС."""
    user = getpass.getuser()
    host = socket.gethostname()
    return WINDOW_TITLE_TEMPLATE.format(user=user, host=host)


def build_prompt(cwd: str) -> str:
    """Формирует строку приглашения с учетом текущей директории."""
    user = getpass.getuser()
    host = socket.gethostname()
    return f"{user}@{host}:{cwd}$ "


class ShellApp(ctk.CTk):
    """Главное окно эмулятора."""

    def __init__(self, config: Config, state: ShellState) -> None:
        super().__init__()
        self.config = config
        # Используем имя shell_state, чтобы не перекрывать встроенный метод tkinter .state()
        self.shell_state = state
        self.title(build_title())
        self.geometry(WINDOW_SIZE)
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Создает элементы интерфейса."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.output = ctk.CTkTextbox(self, font=(FONT_FAMILY, FONT_SIZE), wrap="word")
        self.output.pack(fill="both", expand=True, padx=PADDING, pady=(PADDING, 0))
        self.output.configure(state="disabled")

        self.entry = ctk.CTkEntry(
            self,
            font=(FONT_FAMILY, FONT_SIZE),
            placeholder_text="Type a command (try: ls, cd, history, clear, exit)",
        )
        self.entry.pack(fill="x", padx=PADDING, pady=PADDING)
        self.entry.bind("<Return>", self._on_submit)
        self.entry.focus_set()

        self._append(f"VFS: {self.config.vfs_path}\n")
        self._append(build_prompt(self.shell_state.cwd))

    def _append(self, text: str) -> None:
        """Добавляет текст в окно вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _clear_output(self) -> None:
        """Полностью очищает поле вывода."""
        self.output.configure(state="normal")
        self.output.delete("1.0", "end")
        self.output.configure(state="disabled")

    def _on_submit(self, _event) -> None:
        """Обрабатывает нажатие Enter."""
        raw = self.entry.get()
        self.entry.delete(0, "end")

        self._append(raw + "\n")

        command, _ = parse_input(raw)
        if is_exit(command):
            self._append(execute(raw, self.shell_state) + "\n")
            self.after(SCRIPT_REPLAY_DELAY_MS, self.destroy)
            return

        result = execute(raw, self.shell_state)
        if result == "__CLEAR__":
            self._clear_output()
        elif result:
            self._append(result + "\n")

        self._append(build_prompt(self.shell_state.cwd))

    def replay_script(self) -> None:
        """Проигрывает стартовый скрипт."""
        if not self.config.script_path:
            return
        pairs = run_script(self.config.script_path, self.shell_state)
        delay = SCRIPT_REPLAY_DELAY_MS
        for index, (line, output) in enumerate(pairs):
            self.after(
                delay * (index + 1),
                self._emit_pair,
                line,
                output,
                index == len(pairs) - 1,
            )

    def _emit_pair(self, line: str, result: str, is_last: bool) -> None:
        """Печатает шаг скрипта."""
        self._append(line + "\n")
        if result == "__CLEAR__":
            self._clear_output()
        elif result:
            self._append(result + "\n")

        command, _ = parse_input(line)
        if is_exit(command):
            self.after(SCRIPT_REPLAY_DELAY_MS, self.destroy)
            return

        self._append(build_prompt(self.shell_state.cwd))
        if is_last:
            self.entry.configure(state="normal")
            self.entry.focus_set()


def main() -> None:
    """Точка входа."""
    config = parse_args(sys.argv[1:])
    print(debug_dump(config))

    try:
        vfs = load_vfs_from_csv(config.vfs_path)
    except VFSError as e:
        print(f"Ошибка загрузки VFS: {e}", file=sys.stderr)
        sys.exit(1)

    state = ShellState(vfs, config.vfs_path)
    app = ShellApp(config, state)
    app.after(200, app.replay_script)
    app.mainloop()


if __name__ == "__main__":
    main()
