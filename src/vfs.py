"""Виртуальная файловая система (VFS) в памяти.

VFS хранится как дерево узлов. Все операции выполняются в памяти,
исходный CSV-файл не модифицируется (кроме команды vfs-save).
"""

from dataclasses import dataclass, field

DIR_TYPE = "dir"
FILE_TYPE = "file"
BASE64_PREFIX = "base64:"
PATH_SEPARATOR = "/"


@dataclass
class VfsNode:
    """Узел VFS: папка или файл."""

    name: str
    node_type: str
    content: str = ""
    children: dict[str, "VfsNode"] = field(default_factory=dict)

    @property
    def is_dir(self) -> bool:
        """Является ли узел папкой."""
        return self.node_type == DIR_TYPE


class VfsError(Exception):
    """Ошибка операций над VFS."""


class Vfs:
    """Виртуальная файловая система в памяти."""

    def __init__(self) -> None:
        self.root = VfsNode(name=PATH_SEPARATOR, node_type=DIR_TYPE)

    def add_dir(self, path: str) -> None:
        """Создаёт папку по указанному пути, включая родителей."""
        parts = self._split(path)
        node = self.root
        for part in parts:
            node = node.children.setdefault(
                part, VfsNode(name=part, node_type=DIR_TYPE)
            )

    def add_file(self, path: str, content: str) -> None:
        """Создаёт файл по указанному пути."""
        parts = self._split(path)
        if not parts:
            raise VfsError("Некорректный путь файла")
        parent = self._ensure_parent(parts[:-1])
        parent.children[parts[-1]] = VfsNode(
            name=parts[-1], node_type=FILE_TYPE, content=content
        )

    def get(self, path: str) -> VfsNode | None:
        """Возвращает узел по пути или None, если он не найден."""
        node = self.root
        for part in self._split(path):
            if not node.is_dir or part not in node.children:
                return None
            node = node.children[part]
        return node

    def list_dir(self, path: str) -> list[str]:
        """Возвращает имена детей папки по указанному пути."""
        node = self.get(path)
        if node is None:
            raise VfsError(f"Путь не найден: {path}")
        if not node.is_dir:
            raise VfsError(f"Не папка: {path}")
        return sorted(node.children.keys())

    def to_rows(self) -> list[dict[str, str]]:
        """Сериализует VFS в список строк для CSV-сохранения."""
        rows: list[dict[str, str]] = []
        self._walk(self.root, "", rows)
        return rows

    def _walk(self, node: VfsNode, prefix: str, rows: list[dict[str, str]]) -> None:
        """Рекурсивно обходит дерево и собирает строки."""
        for name, child in sorted(node.children.items()):
            path = (
                f"{prefix}{PATH_SEPARATOR}{name}"
                if prefix
                else f"{PATH_SEPARATOR}{name}"
            )
            rows.append(
                {"type": child.node_type, "path": path, "content": child.content}
            )
            if child.is_dir:
                self._walk(child, path, rows)

    def _ensure_parent(self, parts: list[str]) -> VfsNode:
        """Гарантирует, что все родительские папки существуют."""
        node = self.root
        for part in parts:
            existing = node.children.get(part)
            if existing is None:
                existing = VfsNode(name=part, node_type=DIR_TYPE)
                node.children[part] = existing
            node = existing
        return node

    @staticmethod
    def _split(path: str) -> list[str]:
        """Разбивает путь на компоненты, отбрасывая пустые части."""
        return [p for p in path.split(PATH_SEPARATOR) if p]
