"""Точка входа GUI-эмулятора оболочки."""

import getpass
import socket
import sys

import customtkinter as ctk

from .config import Config, debug_dump, parse_args
from .shell import execute, is_exit, run_script
from .vfs import Vfs, VfsError
from .vfs_io import load_vfs

WINDOW_TITLE_TEMPLATE = "Shell Emulator - [{user}@{host}]"
WINDOW_SIZE = "900x600"
PROMPT_TEMPLATE = "{user}@{host}:{cwd}$ "
FONT_FAMILY = "JetBrains Mono"
FONT_SIZE = 14
PADDING = 10
SCRIPT_REPLAY_DELAY_MS = 400
INITIAL_CWD = "/"


def build_title() -> str:
    """Формирует заголовок окна из реальных данных ОС."""
    user = getpass.getuser()
    host = socket.gethostname()
    return WINDOW_TITLE_TEMPLATE.format(user=user, host=host)


def build_prompt(cwd: str) -> str:
    """Формирует строку приглашения оболочки с учётом cwd."""
    user = getpass.getuser()
    host = socket.gethostname()
    return PROMPT_TEMPLATE.format(user=user, host=host, cwd=cwd)


class ShellApp(ctk.CTk):
    """Главное окно приложения с интерфейсом эмулятора терминала."""

    def __init__(self, config: Config, vfs: Vfs) -> None:
        super().__init__()
        self.config = config
        self.vfs = vfs
        self.cwd = INITIAL_CWD
        self.title(build_title())
        self.geometry(WINDOW_SIZE)
        self._build_widgets()

    def _build_widgets(self) -> None:
        """Создаёт и размещает все виджеты интерфейса."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.output = ctk.CTkTextbox(self, font=(FONT_FAMILY, FONT_SIZE), wrap="word")
        self.output.pack(fill="both", expand=True, padx=PADDING, pady=(PADDING, 0))
        self.output.configure(state="disabled")

        self.entry = ctk.CTkEntry(
            self,
            font=(FONT_FAMILY, FONT_SIZE),
            placeholder_text="Type a command and press Enter (try: ls, cd, vfs-save, exit)",
        )
        self.entry.pack(fill="x", padx=PADDING, pady=PADDING)
        self.entry.bind("<Return>", self._on_submit)
        self.entry.focus_set()

        self._append(self._prompt())

    def _prompt(self) -> str:
        """Возвращает текущее приглашение оболочки."""
        return build_prompt(self.cwd)

    def _append(self, text: str) -> None:
        """Добавляет текст в область вывода."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _on_submit(self, _event) -> None:
        """Обрабатывает Enter: читает ввод, выполняет его, печатает результат."""
        raw = self.entry.get()
        self.entry.delete(0, "end")
        self._append(raw + "\n")

        command, _ = parse_input_safe(raw)
        output, new_cwd = execute(raw, self.vfs, self.cwd)
        self.cwd = new_cwd
        if output:
            self._append(output + "\n")

        if is_exit(command):
            self.after(SCRIPT_REPLAY_DELAY_MS, self.destroy)
            return

        self._append(self._prompt())

    def replay_script(self) -> None:
        """Воспроизводит стартовый скрипт как имитацию диалога."""
        if not self.config.script_path:
            return
        pairs = run_script(self.config.script_path, self.vfs)
        delay = SCRIPT_REPLAY_DELAY_MS
        for index, (line, output) in enumerate(pairs):
            self.after(
                delay * (index + 1),
                self._emit_pair,
                line,
                output,
                index == len(pairs) - 1,
            )

    def _emit_pair(self, line: str, output: str, is_last: bool) -> None:
        """Печатает одну пару (ввод, вывод), имитируя сессию."""
        self._append(line + "\n")
        if output:
            self._append(output + "\n")
        self._append(self._prompt())
        if is_last:
            self.entry.configure(state="normal")
            self.entry.focus_set()


def parse_input_safe(raw: str):
    """Безопасно извлекает имя команды из строки."""
    parts = raw.strip().split()
    return (parts[0] if parts else "", parts[1:] if parts else [])


def main() -> None:
    """Запускает GUI-эмулятор оболочки."""
    config = parse_args(sys.argv[1:])
    print(debug_dump(config))

    try:
        vfs = load_vfs(config.vfs_path)
    except VfsError as exc:
        print(f"Ошибка загрузки VFS: {exc}")
        return

    app = ShellApp(config, vfs)
    app.after(200, app.replay_script)
    app.mainloop()


if __name__ == "__main__":
    main()
