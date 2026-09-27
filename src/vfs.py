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

    def remove_dir(self, path: str) -> None:
        """Удаляет пустую папку по указанному пути.

        Поднимает VfsError, если путь не существует, это не папка,
        это корень или папка не пуста.
        """
        parts = self._split(path)
        if not parts:
            raise VfsError("Нельзя удалить корень")
        parent = self.get(self._parent_path(parts))
        if parent is None or not parent.is_dir:
            raise VfsError(f"Путь не найден: {path}")
        target = parent.children.get(parts[-1])
        if target is None:
            raise VfsError(f"Путь не найден: {path}")
        if not target.is_dir:
            raise VfsError(f"Не папка: {path}")
        if target.children:
            raise VfsError(f"Папка не пуста: {path}")
        del parent.children[parts[-1]]

    def move(self, src: str, dst: str) -> None:
        """Перемещает или переименовывает узел VFS.

        Если dst — существующая папка, узел перемещается внутрь неё
        под тем же именем. Иначе dst трактуется как новый путь узла.
        """
        src_parts = self._split(src)
        if not src_parts:
            raise VfsError("Нельзя переместить корень")

        node = self.get(src)
        if node is None:
            raise VfsError(f"Источник не найден: {src}")

        dst_parts = self._split(dst)
        if not dst_parts:
            raise VfsError("Некорректное назначение")

        # Если dst — существующая папка, кладём внутрь неё под тем же именем
        dst_node = self.get(dst)
        if dst_node is not None and dst_node.is_dir:
            dst_parts = dst_parts + [src_parts[-1]]

        src_abs = PATH_SEPARATOR + PATH_SEPARATOR.join(src_parts)
        dst_abs = PATH_SEPARATOR + PATH_SEPARATOR.join(dst_parts)

        # Проверка: перемещаем папку внутрь себя или своего потомка
        if node.is_dir and (
            dst_abs == src_abs or dst_abs.startswith(src_abs + PATH_SEPARATOR)
        ):
            raise VfsError("Нельзя переместить папку внутрь себя")

        # Если назначение уже существует — ошибка (без перезаписи)
        if self.get(dst_abs) is not None:
            raise VfsError(f"Назначение уже существует: {dst}")

        src_parent = self.get(self._parent_path(src_parts))
        dst_parent = self._ensure_parent(dst_parts[:-1])

        if src_parent is None or dst_parent is None:
            raise VfsError("Не удалось найти родительский каталог")

        del src_parent.children[src_parts[-1]]
        node.name = dst_parts[-1]
        dst_parent.children[dst_parts[-1]] = node

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
    def _parent_path(parts: list[str]) -> str:
        """Возвращает путь родителя для разобранного пути."""
        if len(parts) <= 1:
            return PATH_SEPARATOR
        return PATH_SEPARATOR + PATH_SEPARATOR.join(parts[:-1])

    @staticmethod
    def _split(path: str) -> list[str]:
        """Разбивает путь на компоненты, отбрасывая пустые части."""
        return [p for p in path.split(PATH_SEPARATOR) if p]
