"""Конфигурация эмулятора оболочки через командную строку."""

import argparse
import os
from dataclasses import dataclass

DEFAULT_VFS_PATH = "./vfs/minimal.csv"
DEFAULT_SCRIPT_PATH = ""


@dataclass
class Config:
    """Итоговая конфигурация эмулятора во время выполнения."""

    vfs_path: str
    script_path: str


def build_parser() -> argparse.ArgumentParser:
    """Создаёт парсер аргументов командной строки."""
    parser = argparse.ArgumentParser(
        prog="shell-emulator",
        description="GUI-эмулятор UNIX-подобной оболочки (учебный проект).",
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        default=DEFAULT_VFS_PATH,
        help="Путь к CSV-файлу виртуальной файловой системы.",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        default=DEFAULT_SCRIPT_PATH,
        help="Путь к стартовому скрипту с командами эмулятора.",
    )
    return parser


def parse_args(argv=None) -> Config:
    """Разбирает аргументы CLI и возвращает объект Config."""
    parser = build_parser()
    args = parser.parse_args(argv)
    vfs_path = os.path.abspath(args.vfs_path)
    script_path = _resolve_script_path(args.script_path)
    return Config(vfs_path=vfs_path, script_path=script_path)


def debug_dump(config: Config) -> str:
    """Возвращает отладочную строку со всеми итоговыми параметрами."""
    vfs_exists = os.path.isfile(config.vfs_path)
    script_display = config.script_path or "(не задан)"
    script_exists = _script_exists(config.script_path)
    lines = [
        "=== Конфигурация эмулятора оболочки ===",
        f"CSV VFS        : {config.vfs_path}",
        f"VFS существует : {vfs_exists}",
        f"Путь к скрипту : {script_display}",
        f"Файл скрипта   : {script_exists}",
        "======================================",
    ]
    return "\n".join(lines)


def _resolve_script_path(raw: str) -> str:
    """Возвращает абсолютный путь к скрипту или пустую строку."""
    return os.path.abspath(raw) if raw else ""


def _script_exists(path: str) -> bool:
    """Возвращает True, если скрипт задан и существует."""
    return bool(path) and os.path.isfile(path)
