"""Загрузка и сохранение виртуальной файловой системы (VFS) из/в CSV."""

import csv
import os

from .vfs import VirtualFileSystem


class VFSError(
    Exception,
):
    """Ошибка при работе с VFS."""


def load_vfs_from_csv(csv_path: str) -> VirtualFileSystem:
    """Загружает VFS из CSV-файла.

    Выбрасывает VFSError при отсутствии файла или неверном формате.
    """
    if not os.path.exists(csv_path):
        raise VFSError(f"Файл VFS не найден: {csv_path}")

    vfs = VirtualFileSystem()
    try:
        with open(csv_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            # Проверяем наличие обязательных колонок
            if not reader.fieldnames or not {"type", "path"}.issubset(
                reader.fieldnames
            ):
                raise VFSError(
                    f"Неверный формат CSV: отсутствуют колонки type или path в {csv_path}"
                )

            for row in reader:
                node_type = row.get("type", "").strip()
                path = row.get("path", "").strip()
                content = row.get("content", "")

                if not node_type or not path:
                    continue

                if node_type == "dir":
                    vfs.add_node(path, is_dir=True)
                elif node_type == "file":
                    vfs.add_node(path, is_dir=False, content=content)
                else:
                    raise VFSError(
                        f"Неизвестный тип узла VFS '{node_type}' для пути {path}"
                    )
    except csv.Error as e:
        raise VFSError(f"Ошибка чтения CSV файла {csv_path}: {e}")
    except Exception as e:
        if isinstance(e, VFSError):
            raise e
        raise VFSError(f"Не удалось разобрать CSV файл {csv_path}: {e}")

    return vfs


def save_vfs_to_csv(vfs: VirtualFileSystem, csv_path: str) -> None:
    """Сохраняет текущее состояние VFS в CSV-файл на диск в исходном формате."""
    rows = vfs.export_to_csv_rows()
    try:
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        with open(csv_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["type", "path", "content"])
            for row in rows:
                writer.writerow(row)
    except Exception as e:
        raise VFSError(f"Не удалось сохранить VFS в файл {csv_path}: {e}")
