"""Основная логика REPL: разбор ввода, диспетчеризация, запуск скриптов."""

from collections.abc import Callable

from .commands import cmd_cd, cmd_exit, cmd_ls

# Имя команды -> обработчик.
COMMANDS: dict[str, Callable[[list[str], str], str]] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
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


def execute(raw: str, vfs_path: str) -> str:
    """Разбирает и выполняет одну строку пользовательского ввода.

    Возвращает текстовый результат, который нужно показать в консоли.
    Неизвестные команды дают сообщение об ошибке в стиле UNIX.
    """
    command, args = parse_input(raw)

    if not command:
        return ""

    handler = COMMANDS.get(command)
    if handler is None:
        return UNKNOWN_COMMAND_TEMPLATE.format(name=command)

    return handler(args, vfs_path)


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


def run_script(path: str, vfs_path: str) -> list[tuple[str, str]]:
    """Выполняет стартовый скрипт построчно.

    Останавливается на первой строке, вызвавшей ошибку (неизвестная
    команда). Возвращает список пар (ввод, вывод), чтобы GUI мог
    воспроизвести диалог так, как будто пользователь сам всё набирал.
    """
    results: list[tuple[str, str]] = []
    for index, line in enumerate(read_script(path), start=1):
        command, _ = parse_input(line)
        if command not in COMMANDS:
            reason = UNKNOWN_COMMAND_TEMPLATE.format(name=command)
            results.append(
                (line, SCRIPT_ERROR_TEMPLATE.format(line=index, reason=reason))
            )
            break
        output = execute(line, vfs_path)
        results.append((line, output))
        if is_exit(command):
            break
    return results
