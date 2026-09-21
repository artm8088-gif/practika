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
    return Config(
        vfs_path=os.path.abspath(args.vfs_path),
        script_path=os.path.abspath(args.script_path) if args.script_path else "",
    )


def debug_dump(config: Config) -> str:
    """Возвращает отладочную строку со всеми итоговыми параметрами."""
    lines = [
        "=== Конфигурация эмулятора оболочки ===",
        f"CSV VFS        : {config.vfs_path}",
        f"VFS существует : {os.path.isfile(config.vfs_path)}",
        f"Путь к скрипту : {config.script_path or '(не задан)'}",
        f"Файл скрипта   : {os.path.isfile(config.script_path) if config.script_path else False}",
        "======================================",
    ]
    return "\n".join(lines)
