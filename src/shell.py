"""Основная логика REPL: разбор ввода, диспетчеризация, запуск скриптов с VFS и состоянием."""

from collections.abc import Callable

from .commands import cmd_cd, cmd_clear, cmd_exit, cmd_history, cmd_ls, cmd_vfs_save
from .vfs import VirtualFileSystem


class ShellState:
    """Хранит текущее состояние сессии (путь, VFS, историю команд)."""

    def __init__(self, vfs: VirtualFileSystem, vfs_path: str) -> None:
        self.vfs = vfs
        self.vfs_path = vfs_path
        self.cwd: str = "/"
        self.history: list[str] = []

    def add_history(self, command: str) -> None:
        """Добавляет команду в историю."""
        stripped = command.strip()
        if stripped:
            self.history.append(stripped)

    def resolve_path(self, path_arg: str) -> str:
        """Превращает относительный или абсолютный путь в канонический абсолютный."""
        if not path_arg or path_arg == ".":
            return self.cwd

        if path_arg.startswith("/"):
            parts = [p for p in path_arg.split("/") if p]
        else:
            base_parts = [p for p in self.cwd.split("/") if p]
            rel_parts = [p for p in path_arg.split("/") if p]
            parts = base_parts + rel_parts

        resolved_parts: list[str] = []
        for part in parts:
            if part == "..":
                if resolved_parts:
                    resolved_parts.pop()
            elif part != ".":
                resolved_parts.append(part)

        return "/" + "/".join(resolved_parts)


# Имя команды -> обработчик. Принимает (args, state)
COMMANDS: dict[str, Callable[[list[str], ShellState], str]] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "history": cmd_history,
    "clear": cmd_clear,
    "vfs-save": cmd_vfs_save,
    "exit": cmd_exit,
}

UNKNOWN_COMMAND_TEMPLATE = "shell: command not found: {name}"
SCRIPT_ERROR_TEMPLATE = "shell: script aborted at line {line}: {reason}"


def parse_input(raw: str) -> tuple[str, list[str]]:
    """Разбирает ввод пользователя на имя команды и список аргументов."""
    parts = raw.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def is_exit(command: str) -> bool:
    """Возвращает True, если команда запрашивает завершение оболочки."""
    return command == "exit"


def execute(raw: str, state: ShellState) -> str:
    """Разбирает и выполняет одну строку пользовательского ввода с учетом состояния."""
    command, args = parse_input(raw)

    if not command:
        return ""

    handler = COMMANDS.get(command)
    if handler is None:
        return UNKNOWN_COMMAND_TEMPLATE.format(name=command)

    state.add_history(raw)
    return handler(args, state)


def read_script(path: str) -> list[str]:
    """Читает стартовый скрипт и возвращает непустые строки без комментариев."""
    lines: list[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if not stripped or stripped.startswith("#"):
                continue
            lines.append(stripped)
    return lines


def run_script(path: str, state: ShellState) -> list[tuple[str, str]]:
    """Выполняет стартовый скрипт построчно с остановкой на первой ошибке."""
    results: list[tuple[str, str]] = []
    for index, line in enumerate(read_script(path), start=1):
        command, _ = parse_input(line)
        if command not in COMMANDS:
            reason = UNKNOWN_COMMAND_TEMPLATE.format(name=command)
            results.append(
                (line, SCRIPT_ERROR_TEMPLATE.format(line=index, reason=reason))
            )
            break
        output = execute(line, state)
        results.append((line, output))
        if is_exit(command):
            break
    return results
