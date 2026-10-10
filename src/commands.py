"""Реализация команд эмулятора оболочки для этапа 3 (и базовых заглушек)."""

from .vfs_io import VFSError, save_vfs_to_csv

VFS_PREFIX = "[vfs]"


def cmd_ls(args: list[str], vfs_path: str, vfs=None) -> str:
    """Команда `ls`: выводит содержимое папки из VFS или заглушку."""
    if vfs is not None:
        # Для этапа 3 используем реальную VFS, если она передана
        target_path = args[0] if args else "/"
        node = vfs.get_node(target_path)
        if node is None:
            return f"ls: {target_path}: No such file or directory"
        if not node.is_dir:
            return target_path
        children = vfs.list_dir(target_path)
        return "\n".join(children) if children else ""

    # Заглушка (на случай вызова без VFS)
    return f"ls: args={args}"


def cmd_cd(args: list[str], vfs_path: str, vfs=None) -> str:
    """Команда `cd`."""
    if vfs is not None:
        if not args:
            return ""
        target_path = args[0]
        node = vfs.get_node(target_path)
        if node is None:
            return f"cd: {target_path}: No such file or directory"
        if not node.is_dir:
            return f"cd: {target_path}: Not a directory"
        return ""

    return f"cd: args={args}"


def cmd_vfs_save(args: list[str], vfs_path: str, vfs=None) -> str:
    """Команда `vfs-save <путь>`: сохраняет состояние VFS на диск в исходном формате."""
    if not args:
        return "vfs-save: missing file path argument"

    dest_path = args[0]
    if vfs is None:
        return "vfs-save: VFS is not loaded"

    try:
        save_vfs_to_csv(vfs, dest_path)
        return f"VFS successfully saved to {dest_path}"
    except VFSError as e:
        return f"vfs-save error: {e}"


def cmd_exit(args: list[str], vfs_path: str, vfs=None) -> str:
    """Сигнал оболочке завершить работу."""
    return "exit: shutting down..."
