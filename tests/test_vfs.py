"""Тесты модели виртуальной файловой системы."""

import pytest

from src.vfs import Vfs, VfsError


def test_add_dir_and_list():
    """Создание папки и просмотр её содержимого."""
    vfs = Vfs()
    vfs.add_dir("/home/mark")
    assert vfs.list_dir("/home") == ["mark"]


def test_add_file_and_get():
    """Создание файла и его получение."""
    vfs = Vfs()
    vfs.add_file("/tmp/notes.txt", "hello")
    node = vfs.get("/tmp/notes.txt")
    assert node is not None
    assert node.content == "hello"


def test_remove_empty_dir():
    """Удаление пустой папки."""
    vfs = Vfs()
    vfs.add_dir("/tmp/empty")
    vfs.remove_dir("/tmp/empty")
    assert vfs.get("/tmp/empty") is None


def test_remove_non_empty_dir_raises():
    """Нельзя удалить непустую папку."""
    vfs = Vfs()
    vfs.add_file("/tmp/data.txt", "x")
    with pytest.raises(VfsError):
        vfs.remove_dir("/tmp")


def test_remove_root_raises():
    """Нельзя удалить корень."""
    vfs = Vfs()
    with pytest.raises(VfsError):
        vfs.remove_dir("/")


def test_move_rename():
    """Переименование файла."""
    vfs = Vfs()
    vfs.add_file("/tmp/a.txt", "x")
    vfs.move("/tmp/a.txt", "/tmp/b.txt")
    assert vfs.get("/tmp/a.txt") is None
    assert vfs.get("/tmp/b.txt") is not None


def test_move_into_dir():
    """Перемещение файла в существующую папку."""
    vfs = Vfs()
    vfs.add_file("/tmp/a.txt", "x")
    vfs.add_dir("/tmp/sub")
    vfs.move("/tmp/a.txt", "/tmp/sub")
    assert vfs.get("/tmp/sub/a.txt") is not None


def test_move_into_itself_raises():
    """Нельзя переместить папку внутрь себя."""
    vfs = Vfs()
    vfs.add_dir("/tmp/a/b")
    with pytest.raises(VfsError):
        vfs.move("/tmp/a", "/tmp/a/b")
