"""Загрузка и сохранение VFS в формате CSV.

Формат:
    type,path,content
    dir,/home,
    file,/home/mark/notes.txt,Hello world
    file,/home/mark/photo.png,base64:iVBORw0KGgo=

Вложенность задаётся через полный путь, а не через отдельные
родительские записи.
"""

import csv
from collections.abc import Sequence

from .vfs import BASE64_PREFIX, DIR_TYPE, FILE_TYPE, Vfs, VfsError

REQUIRED_COLUMNS = ("type", "path", "content")
VALID_TYPES = {DIR_TYPE, FILE_TYPE}


def load_vfs(path: str) -> Vfs:
    """Загружает VFS из CSV-файла.

    Поднимает VfsError, если файл не найден или формат неверен.
    """
    try:
        with open(path, "r", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            return _build_from_rows(reader.fieldnames, list(reader))
    except FileNotFoundError:
        raise VfsError(f"Файл VFS не найден: {path}")
    except OSError as exc:
        raise VfsError(f"Ошибка чтения файла VFS: {exc}")


def save_vfs(vfs: Vfs, path: str) -> None:
    """Сохраняет состояние VFS в CSV-файл."""
    try:
        with open(path, "w", encoding="utf-8", newline="") as fh:
            writer: csv.DictWriter[str] = csv.DictWriter(
                fh, fieldnames=list(REQUIRED_COLUMNS)
            )
            writer.writeheader()
            for row in vfs.to_rows():
                writer.writerow(row)
    except OSError as exc:
        raise VfsError(f"Ошибка записи файла VFS: {exc}")


def _build_from_rows(
    fieldnames: Sequence[str] | None, rows: list[dict[str, str]]
) -> Vfs:
    """Проверяет формат и собирает VFS из строк CSV."""
    if not fieldnames or not set(REQUIRED_COLUMNS).issubset(fieldnames):
        raise VfsError("Неверный формат CSV: нужны колонки type, path, content")

    vfs = Vfs()
    for index, row in enumerate(rows, start=2):
        _apply_row(vfs, row, index)
    return vfs


def _apply_row(vfs: Vfs, row: dict[str, str], line_no: int) -> None:
    """Применяет одну строку CSV к VFS."""
    node_type = (row.get("type") or "").strip()
    path = (row.get("path") or "").strip()
    content = row.get("content") or ""

    if node_type not in VALID_TYPES:
        raise VfsError(f"Строка {line_no}: неизвестный тип '{node_type}'")
    if not path:
        raise VfsError(f"Строка {line_no}: пустой путь")

    if node_type == DIR_TYPE:
        vfs.add_dir(path)
        return

    if content.startswith(BASE64_PREFIX):
        # Двоичные данные. Для этапа 3 достаточно сохранить как есть,
        # декодирование не требуется для команд ls/cd.
        vfs.add_file(path, content)
        return

    vfs.add_file(path, content)
