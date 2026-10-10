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

    def add_node(self, path: str, is_dir: bool, content: str = "") -> None:
        """Добавляет узел (файл или папку) по абсолютному пути.

        Автоматически создаёт промежуточные директории, если они отсутствуют.
        """
        parts = [p for p in path.split("/") if p]
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

        parts = [p for p in path.split("/") if p]
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
