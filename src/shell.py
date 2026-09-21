"""Основная логика REPL: разбор ввода, диспетчеризация, запуск скриптов."""

from collections.abc import Callable

from .commands import (
    CommandError,
    cmd_cd,
    cmd_exit,
    cmd_ls,
    cmd_vfs_save,
)
from .vfs import Vfs

CommandHandler = Callable[[list[str], Vfs, str], tuple[str, str]]

COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
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


def execute(raw: str, vfs: Vfs, cwd: str) -> tuple[str, str]:
    """Выполняет одну строку пользовательского ввода.

    Возвращает пару (вывод, новый рабочий каталог).
    """
    command, args = parse_input(raw)
    if not command:
        return "", cwd

    handler = COMMANDS.get(command)
    if handler is None:
        return UNKNOWN_COMMAND_TEMPLATE.format(name=command), cwd

    try:
        return handler(args, vfs, cwd)
    except CommandError as exc:
        return str(exc), cwd


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


def run_script(path: str, vfs: Vfs) -> list[tuple[str, str]]:
    """Выполняет стартовый скрипт построчно.

    Останавливается на первой строке, вызвавшей ошибку.
    Возвращает список пар (ввод, вывод).
    """
    results: list[tuple[str, str]] = []
    cwd = "/"
    for index, line in enumerate(read_script(path), start=1):
        command, _ = parse_input(line)
        if command not in COMMANDS:
            reason = UNKNOWN_COMMAND_TEMPLATE.format(name=command)
            results.append(
                (line, SCRIPT_ERROR_TEMPLATE.format(line=index, reason=reason))
            )
            break
        output, cwd = execute(line, vfs, cwd)
        results.append((line, output))
        if is_exit(command):
            break
    return results
