"""Основная логика REPL: разбор ввода, диспетчеризация, запуск скриптов с VFS."""

from collections.abc import Callable
from typing import Any

from .commands import cmd_cd, cmd_exit, cmd_ls, cmd_vfs_save
from .vfs import VirtualFileSystem

# Имя команды -> обработчик.
COMMANDS: dict[str, Callable[[list[str], str, Any], str]] = {
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


def execute(raw: str, vfs_path: str, vfs: VirtualFileSystem | None = None) -> str:
    """Разбирает и выполняет одну строку пользовательского ввода с учетом VFS."""
    command, args = parse_input(raw)

    if not command:
        return ""

    handler = COMMANDS.get(command)
    if handler is None:
        return UNKNOWN_COMMAND_TEMPLATE.format(name=command)

    return handler(args, vfs_path, vfs)


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


def run_script(
    path: str, vfs_path: str, vfs: VirtualFileSystem | None = None
) -> list[tuple[str, str]]:
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
        output = execute(line, vfs_path, vfs)
        results.append((line, output))
        if is_exit(command):
            break
    return results
