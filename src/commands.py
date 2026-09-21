"""Заглушки команд эмулятора оболочки.

Каждая команда принимает список аргументов, разобранных из ввода
пользователя, и возвращает строку, которая будет показана в окне
терминала. Команды `ls` и `cd` знают о текущем пути VFS.
"""

VFS_PREFIX = "[vfs]"


def cmd_ls(args: list[str], vfs_path: str) -> str:
    """Заглушка команды UNIX `ls`.

    Сообщает текущий путь VFS и полученные аргументы.
    """
    return f"ls: vfs={vfs_path} {VFS_PREFIX} args={args}"


def cmd_cd(args: list[str], vfs_path: str) -> str:
    """Заглушка команды UNIX `cd`.

    Сообщает текущий путь VFS и полученные аргументы.
    """
    return f"cd: vfs={vfs_path} {VFS_PREFIX} args={args}"


def cmd_exit(args: list[str], vfs_path: str) -> str:
    """Сигнал оболочке завершить работу."""
    return "exit: shutting down..."
