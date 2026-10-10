"""Модель виртуальной файловой системы (VFS) в памяти."""

from dataclasses import dataclass, field


@dataclass
class VFSNode:
    """Узел VFS: файл или директория."""

    path: str
    is_dir: bool
    content: str = ""  # Для файлов: обычный текст или префикс "base64:..."
    children: dict[str, "VFSNode"] = field(default_factory=dict)


class VirtualFileSystem:
    """Виртуальная файловая система, работающая полностью в памяти."""

    def __init__(self) -> None:
        # Корневой узел
        self.root = VFSNode(path="/", is_dir=True)

    def _split_path(self, path: str) -> list[str]:
        """Вспомогательный метод для разбиения пути на компоненты."""
        return [p for p in path.split("/") if p]

    def add_node(self, path: str, is_dir: bool, content: str = "") -> None:
        """Добавляет узел (файл или папку) по абсолютному пути.

        Автоматически создаёт промежуточные директории, если они отсутствуют.
        """
        parts = self._split_path(path)
        current = self.root

        # Проходим по всем элементам пути, кроме последнего
        current_path = ""
        for part in parts[:-1]:
            current_path += f"/{part}"
            if part not in current.children:
                current.children[part] = VFSNode(path=current_path, is_dir=True)
            current = current.children[part]

        # Обрабатываем последний элемент пути
        if parts:
            last_part = parts[-1]
            full_path = f"{current.path.rstrip('/')}/{last_part}"
            if is_dir:
                if last_part not in current.children:
                    current.children[last_part] = VFSNode(path=full_path, is_dir=True)
            else:
                current.children[last_part] = VFSNode(
                    path=full_path, is_dir=False, content=content
                )

    def get_node(self, path: str) -> VFSNode | None:
        """Возвращает узел по абсолютному пути или None, если он не найден."""
        if path == "/":
            return self.root

        parts = self._split_path(path)
        current = self.root
        for part in parts:
            if part not in current.children:
                return None
            current = current.children[part]
        return current

    def list_dir(self, path: str) -> list[str]:
        """Возвращает список имен файлов/папок в указанной директории."""
        node = self.get_node(path)
        if node is None or not node.is_dir:
            return []
        return sorted(list(node.children.keys()))

    def remove_node(self, path: str) -> bool:
        """Удаляет узел (файл или папку) по указанному пути."""
        normalized = "/" + "/".join(self._split_path(path))
        if normalized == "/":
            return False  # Корень удалять нельзя

        parts = self._split_path(path)
        if not parts:
            return False

        parent_path = "/" + "/".join(parts[:-1])
        parent_node = self.get_node(parent_path)
        target_name = parts[-1]

        if parent_node is None or target_name not in parent_node.children:
            return False

        target_node = parent_node.children[target_name]
        if target_node.is_dir and target_node.children:
            raise ValueError("Directory not empty")

        del parent_node.children[target_name]
        return True

    def move_node(self, src_path: str, dest_path: str) -> bool:
        """Перемещает или переименовывает узел из src в dest."""
        src_parts = self._split_path(src_path)
        if not src_parts or "/" + "/".join(src_parts) == "/":
            return False

        src_parent_path = "/" + "/".join(src_parts[:-1])
        src_parent = self.get_node(src_parent_path)
        src_name = src_parts[-1]

        if src_parent is None or src_name not in src_parent.children:
            return False

        src_node = src_parent.children[src_name]

        dest_parts = self._split_path(dest_path)
        dest_node = self.get_node("/" + "/".join(dest_parts))

        if dest_node and dest_node.is_dir:
            dest_parent = dest_node
            dest_name = src_name
        else:
            if not dest_parts:
                return False
            dest_parent_path = "/" + "/".join(dest_parts[:-1])
            dest_parent = self.get_node(dest_parent_path)
            dest_name = dest_parts[-1]

        if dest_parent is None or dest_name in dest_parent.children:
            return False

        del src_parent.children[src_name]
        src_node.path = f"{dest_parent.path.rstrip('/')}/{dest_name}"
        dest_parent.children[dest_name] = src_node

        return True

    def export_to_csv_rows(self) -> list[tuple[str, str, str]]:
        """Экспортирует все узлы VFS в плоский список строк для CSV (type, path, content)."""
        rows = []

        def _traverse(node: VFSNode) -> None:
            for child in sorted(node.children.values(), key=lambda n: n.path):
                node_type = "dir" if child.is_dir else "file"
                rows.append(
                    (node_type, child.path, child.content if not child.is_dir else "")
                )
                if child.is_dir:
                    _traverse(child)

        _traverse(self.root)
        return rows
