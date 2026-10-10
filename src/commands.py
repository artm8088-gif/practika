"""Реализация команд эмулятора оболочки для этапа 5."""

from .vfs_io import VFSError, save_vfs_to_csv


def cmd_ls(args: list[str], state) -> str:
    """Команда `ls [путь]`: выводит содержимое каталога."""
    target_arg = args[0] if args else "."
    resolved_path = state.resolve_path(target_arg)

    node = state.vfs.get_node(resolved_path)
    if node is None:
        return f"ls: {target_arg}: No such file or directory"
    if not node.is_dir:
        return resolved_path

    children = state.vfs.list_dir(resolved_path)
    return "\n".join(children) if children else ""


def cmd_cd(args: list[str], state) -> str:
    """Команда `cd [путь]`: смена текущего каталога."""
    if not args:
        state.cwd = "/"
        return ""

    target_arg = args[0]
    resolved_path = state.resolve_path(target_arg)

    node = state.vfs.get_node(resolved_path)
    if node is None:
        return f"cd: {target_arg}: No such file or directory"
    if not node.is_dir:
        return f"cd: {target_arg}: Not a directory"

    state.cwd = resolved_path
    return ""


def cmd_history(args: list[str], state) -> str:
    """Команда `history`: вывод истории введенных команд с нумерацией."""
    lines = ["История команд:"]
    for idx, cmd in enumerate(state.history, start=1):
        lines.append(f"  {idx:3d}  {cmd}")
    return "\n".join(lines)


def cmd_clear(args: list[str], state) -> str:
    """Команда `clear`: очистка экрана (сигнализируется GUI)."""
    return "__CLEAR__"


def cmd_vfs_save(args: list[str], state) -> str:
    """Команда `vfs-save <путь>`: сохранение состояния VFS на диск."""
    if not args:
        return "vfs-save: missing file path argument"
    dest_path = args[0]
    try:
        save_vfs_to_csv(state.vfs, dest_path)
        return f"VFS successfully saved to {dest_path}"
    except VFSError as e:
        return f"vfs-save error: {e}"


def cmd_rmdir(args: list[str], state) -> str:
    """Команда `rmdir <путь>`: удаление пустого каталога."""
    if not args:
        return "rmdir: missing operand"

    target_arg = args[0]
    resolved_path = state.resolve_path(target_arg)

    node = state.vfs.get_node(resolved_path)
    if node is None:
        return f"rmdir: failed to remove '{target_arg}': No such file or directory"
    if not node.is_dir:
        return f"rmdir: failed to remove '{target_arg}': Not a directory"

    try:
        success = state.vfs.remove_node(resolved_path)
        if not success:
            return f"rmdir: failed to remove '{target_arg}': Permission denied or root"
    except ValueError:
        return f"rmdir: failed to remove '{target_arg}': Directory not empty"

    return ""


def cmd_mv(args: list[str], state) -> str:
    """Команда `mv <источник> <назначение>`: перемещение или переименование."""
    if len(args) < 2:
        return "mv: missing file operand"

    src_arg = args[0]
    dest_arg = args[1]

    src_resolved = state.resolve_path(src_arg)
    dest_resolved = state.resolve_path(dest_arg)

    node = state.vfs.get_node(src_resolved)
    if node is None:
        return f"mv: cannot stat '{src_arg}': No such file or directory"

    try:
        success = state.vfs.move_node(src_resolved, dest_resolved)
        if not success:
            return f"mv: cannot move '{src_arg}' to '{dest_arg}': Destination exists or invalid"
    except Exception as e:
        return f"mv error: {e}"

    return ""


def cmd_exit(args: list[str], state) -> str:
    """Завершение работы эмулятора."""
    return "exit: shutting down..."
