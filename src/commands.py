"""Реализация команд эмулятора поверх VFS в памяти.

Каждая команда принимает список аргументов, VFS, текущий рабочий
каталог и историю команд, а возвращает CommandResult.
"""

from dataclasses import dataclass

from .vfs import Vfs, VfsError
from .vfs_io import save_vfs

PATH_SEPARATOR = "/"
HISTORY_HEADER = "История команд:"
MV_ARG_COUNT = 2
VFS_SAVE_ARG_COUNT = 1
RMDIR_ARG_COUNT = 1
CURRENT_DIR = "."
PARENT_DIR = ".."


class CommandError(Exception):
    """Ошибка выполнения команды."""


@dataclass
class CommandResult:
    """Результат выполнения команды."""

    output: str = ""
    cwd: str = "/"
    clear: bool = False
    new_history_entry: str = ""


def cmd_ls(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Реализация UNIX `ls`: список содержимого папки."""
    target = args[0] if args else cwd
    path = _resolve(target, cwd)
    try:
        names = vfs.list_dir(path)
    except VfsError as exc:
        raise CommandError(str(exc))
    return CommandResult(output="\n".join(names), cwd=cwd)


def cmd_cd(
    args: list[str],
    vfs: Vfs,
    cwd: str,
    history: list[str],
) -> CommandResult:
    """Реализация UNIX `cd`: смена текущего каталога."""
    if not args:
        return CommandResult(cwd=PATH_SEPARATOR)
    target = _resolve(args[0], cwd)
    node = vfs.get(target)
    if node is None:
        raise CommandError(f"Нет такого каталога: {args[0]}")
    if not node.is_dir:
        raise CommandError(f"Не каталог: {args[0]}")
    return CommandResult(cwd=_normalize(target))


def cmd_history(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Реализация команды `history`: печатает историю команд."""
    if not history:
        return CommandResult(output="История пуста", cwd=cwd)
    lines = [f"{index:>4}  {cmd}" for index, cmd in enumerate(history, start=1)]
    return CommandResult(output="\n".join([HISTORY_HEADER, *lines]), cwd=cwd)


def cmd_clear(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Реализация команды `clear`: очищает экран эмулятора."""
    return CommandResult(clear=True, cwd=cwd)


def cmd_vfs_save(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Команда `vfs-save <путь>`: сохраняет VFS в CSV-файл."""
    if len(args) < VFS_SAVE_ARG_COUNT:
        raise CommandError("Использование: vfs-save <путь>")
    try:
        save_vfs(vfs, args[0])
    except VfsError as exc:
        raise CommandError(str(exc))
    return CommandResult(output=f"VFS сохранена в {args[0]}", cwd=cwd)


def cmd_exit(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Сигнал оболочке завершить работу."""
    return CommandResult(output="exit: shutting down...", cwd=cwd)


def cmd_rmdir(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Реализация команды `rmdir`: удаляет пустую папку."""
    if len(args) < RMDIR_ARG_COUNT:
        raise CommandError("Использование: rmdir <путь>")
    path = _resolve(args[0], cwd)
    try:
        vfs.remove_dir(path)
    except VfsError as exc:
        raise CommandError(str(exc))
    return CommandResult(output=f"Удалена папка: {path}", cwd=cwd)


def cmd_mv(
    args: list[str], vfs: Vfs, cwd: str, history: list[str]
) -> CommandResult:
    """Реализация команды `mv`: перемещение или переименование."""
    if len(args) != MV_ARG_COUNT:
        raise CommandError("Использование: mv <источник> <назначение>")
    src = _resolve(args[0], cwd)
    dst = _resolve(args[1], cwd)
    try:
        vfs.move(src, dst)
    except VfsError as exc:
        raise CommandError(str(exc))
    return CommandResult(output=f"Перемещено: {src} -> {dst}", cwd=cwd)


def _resolve(target: str, cwd: str) -> str:
    """Приводит относительный путь к абсолютному относительно cwd.

    Поддерживает `.` и `..`.
    """
    if not target:
        return cwd
    base = _split_parts(cwd)
    extra = _split_parts(target)
    parts = extra if target.startswith(PATH_SEPARATOR) else base + extra
    return _join(_collapse(parts))


def _normalize(path: str) -> str:
    """Нормализует путь: убирает дублирующие слэши и висячий слэш."""
    return _join(_split_parts(path))


def _split_parts(path: str) -> list[str]:
    """Разбивает путь на компоненты, отбрасывая пустые части."""
    return [p for p in path.split(PATH_SEPARATOR) if p]


def _join(parts: list[str]) -> str:
    """Собирает абсолютный путь из компонентов."""
    if not parts:
        return PATH_SEPARATOR
    return PATH_SEPARATOR + PATH_SEPARATOR.join(parts)


def _collapse(parts: list[str]) -> list[str]:
    """Обрабатывает `.` и `..`, возвращая нормализованные компоненты."""
    result: list[str] = []
    for part in parts:
        if part == CURRENT_DIR:
            continue
        if part == PARENT_DIR:
            if result:
                result.pop()
            continue
        result.append(part)
    return result
