"""Реализация команд эмулятора поверх VFS в памяти.

Каждая команда принимает список аргументов, VFS и текущий рабочий
каталог, а возвращает пару (вывод, новый рабочий каталог).
"""

from .vfs import Vfs, VfsError
from .vfs_io import save_vfs


class CommandError(Exception):
    """Ошибка выполнения команды."""


def cmd_ls(args: list[str], vfs: Vfs, cwd: str) -> tuple[str, str]:
    """Реализация UNIX `ls`: список содержимого папки."""
    target = args[0] if args else cwd
    path = _resolve(target, cwd)
    try:
        names = vfs.list_dir(path)
    except VfsError as exc:
        raise CommandError(str(exc))
    return ("\n".join(names) if names else ""), cwd


def cmd_cd(args: list[str], vfs: Vfs, cwd: str) -> tuple[str, str]:
    """Реализация UNIX `cd`: смена текущего каталога."""
    if not args:
        return "", "/"
    target = _resolve(args[0], cwd)
    node = vfs.get(target)
    if node is None:
        raise CommandError(f"Нет такого каталога: {args[0]}")
    if not node.is_dir:
        raise CommandError(f"Не каталог: {args[0]}")
    return "", target


def cmd_vfs_save(args: list[str], vfs: Vfs, cwd: str) -> tuple[str, str]:
    """Команда `vfs-save <путь>`: сохраняет VFS в CSV-файл."""
    if not args:
        raise CommandError("Использование: vfs-save <путь>")
    try:
        save_vfs(vfs, args[0])
    except VfsError as exc:
        raise CommandError(str(exc))
    return f"VFS сохранена в {args[0]}", cwd


def cmd_exit(args: list[str], vfs: Vfs, cwd: str) -> tuple[str, str]:
    """Сигнал оболочке завершить работу."""
    return "exit: shutting down...", cwd


def _resolve(target: str, cwd: str) -> str:
    """Приводит относительный путь к абсолютному относительно cwd."""
    if target.startswith("/"):
        return target
    base = cwd.rstrip("/")
    return f"{base}/{target}" if base else f"/{target}"
