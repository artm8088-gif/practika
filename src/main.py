"""Точка входа GUI-эмулятора оболочки."""

import getpass
import socket
import sys

import customtkinter as ctk

from .config import Config, debug_dump, parse_args
from .shell import execute, is_exit, run_script

WINDOW_TITLE_TEMPLATE = "Shell Emulator - [{user}@{host}]"
WINDOW_SIZE = "900x600"
PROMPT_TEMPLATE = "{user}@{host}:~$ "
FONT_FAMILY = "JetBrains Mono"
FONT_SIZE = 14
PADDING = 10
SCRIPT_REPLAY_DELAY_MS = 400


def build_title() -> str:
    """Формирует заголовок окна из реальных данных ОС."""
    user = getpass.getuser()
    host = socket.gethostname()
    return WINDOW_TITLE_TEMPLATE.format(user=user, host=host)


def build_prompt() -> str:
    """Формирует строку приглашения оболочки перед вводом пользователя."""
    user = getpass.getuser()
    host = socket.gethostname()
    return PROMPT_TEMPLATE.format(user=user, host=host)


class ShellApp(ctk.CTk):
    """Главное окно приложения с интерфейсом эмулятора терминала."""

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self.title(build_title())
        self.geometry(WINDOW_SIZE)
        self.prompt = build_prompt()
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
            placeholder_text="Type a command and press Enter (try: ls, cd, exit)",
        )
        self.entry.pack(fill="x", padx=PADDING, pady=PADDING)
        self.entry.bind("<Return>", self._on_submit)
        self.entry.focus_set()

        self._append(self.prompt)

    def _append(self, text: str) -> None:
        """Добавляет текст в область вывода, оставляя её read-only."""
        self.output.configure(state="normal")
        self.output.insert("end", text)
        self.output.see("end")
        self.output.configure(state="disabled")

    def _on_submit(self, _event) -> None:
        """Обрабатывает Enter: читает ввод, выполняет его, печатает результат."""
        raw = self.entry.get()
        self.entry.delete(0, "end")

        self._append(raw + "\n")

        command, _ = (raw.strip().split() + [""])[0], None
        if is_exit(command):
            self._append(execute(raw, self.config.vfs_path) + "\n")
            self.after(SCRIPT_REPLAY_DELAY_MS, self.destroy)
            return

        result = execute(raw, self.config.vfs_path)
        if result:
            self._append(result + "\n")
        self._append(self.prompt)

    def replay_script(self) -> None:
        """Воспроизводит стартовый скрипт как имитацию диалога с пользователем."""
        if not self.config.script_path:
            return
        pairs = run_script(self.config.script_path, self.config.vfs_path)
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
        """Печатает одну пару (ввод, вывод), имитируя сессию пользователя."""
        self._append(line + "\n")
        if output:
            self._append(output + "\n")
        self._append(self.prompt)
        if is_last:
            self.entry.configure(state="normal")
            self.entry.focus_set()


def main() -> None:
    """Запускает GUI-эмулятор оболочки."""
    config = parse_args(sys.argv[1:])
    print(debug_dump(config))
    app = ShellApp(config)
    app.after(200, app.replay_script)
    app.mainloop()


if __name__ == "__main__":
    main()
