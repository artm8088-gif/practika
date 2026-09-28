"""Основная логика REPL: разбор ввода, диспетчеризация, запуск скриптов."""

from collections.abc import Callable
from dataclasses import dataclass, field

from .commands import (
    CommandError,
    CommandResult,
    cmd_cd,
    cmd_clear,
    cmd_exit,
    cmd_history,
    cmd_ls,
    cmd_mv,
    cmd_rmdir,
    cmd_vfs_save,
)
from .vfs import Vfs

CommandHandler = Callable[[list[str], Vfs, str, list[str]], CommandResult]

COMMANDS: dict[str, CommandHandler] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "history": cmd_history,
    "clear": cmd_clear,
    "rmdir": cmd_rmdir,
    "mv": cmd_mv,
    "vfs-save": cmd_vfs_save,
    "exit": cmd_exit,
}


UNKNOWN_COMMAND_TEMPLATE = "shell: command not found: {name}"
SCRIPT_ERROR_TEMPLATE = "shell: script aborted at line {line}: {reason}"
INITIAL_CWD = "/"
COMMENT_MARKER = "#"


@dataclass
class ShellState:
    """Состояние оболочки: текущий каталог и история команд."""

    cwd: str = INITIAL_CWD
    history: list[str] = field(default_factory=list)


def parse_input(raw: str) -> tuple[str, list[str]]:
    """Разбирает ввод, отбрасывая комментарий после #."""
    line = raw.split(COMMENT_MARKER, 1)[0].strip()
    parts = line.split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def is_exit(command: str) -> bool:
    """Возвращает True, если команда запрашивает завершение оболочки."""
    return command == "exit"


def execute(raw: str, vfs: Vfs, state: ShellState) -> CommandResult:
    """Выполняет одну строку пользовательского ввода.

    Обновляет историю команд в state (кроме пустых строк).
    """
    command, args = parse_input(raw)
    if not command:
        return CommandResult(cwd=state.cwd)

    state.history.append(raw.strip())

    if command not in COMMANDS:
        return CommandResult(
            output=UNKNOWN_COMMAND_TEMPLATE.format(name=command),
            cwd=state.cwd,
        )

    try:
        result = COMMANDS[command](args, vfs, state.cwd, state.history)
    except CommandError as exc:
        return CommandResult(output=str(exc), cwd=state.cwd)

    state.cwd = result.cwd
    return result


def read_script(path: str) -> list[str]:
    """Читает стартовый скрипт и возвращает непустые строки без комментариев."""
    lines: list[str] = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            stripped = raw.strip()
            if not stripped or stripped.startswith(COMMENT_MARKER):
                continue
            lines.append(stripped)
    return lines


def run_script(path: str, vfs: Vfs) -> list[tuple[str, CommandResult]]:
    """Выполняет стартовый скрипт построчно.

    Останавливается на первой строке, вызвавшей ошибку.
    Возвращает список пар (ввод, результат).
    """
    results: list[tuple[str, CommandResult]] = []
    state = ShellState()
    for index, line in enumerate(read_script(path), start=1):
        command, _ = parse_input(line)
        if command not in COMMANDS:
            results.append(_script_error(line, index, state.cwd))
            break
        result = execute(line, vfs, state)
        results.append((line, result))
        if is_exit(command):
            break
    return results


def _script_error(line: str, index: int, cwd: str) -> tuple[str, CommandResult]:
    """Формирует пару (строка, результат) для ошибки в скрипте."""
    command, _ = parse_input(line)
    reason = UNKNOWN_COMMAND_TEMPLATE.format(name=command)
    output = SCRIPT_ERROR_TEMPLATE.format(line=index, reason=reason)
    return line, CommandResult(output=output, cwd=cwd)
