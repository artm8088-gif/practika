"""Тесты загрузки и сохранения VFS."""

import pytest

from src.vfs import Vfs, VfsError
from src.vfs_io import load_vfs, save_vfs

CSV_OK = "type,path,content\ndir,/home,\nfile,/home/notes.txt,hello\n"
CSV_BAD_HEADER = "wrong,columns\nfoo,bar\n"
CSV_BAD_TYPE = "type,path,content\nunknown,/tmp/x,\n"


def test_load_ok(tmp_path):
    """Корректный CSV загружается."""
    path = tmp_path / "vfs.csv"
    path.write_text(CSV_OK, encoding="utf-8")
    vfs = load_vfs(str(path))
    assert vfs.get("/home/notes.txt") is not None


def test_load_missing_file():
    """Несуществующий файл даёт VfsError."""
    with pytest.raises(VfsError):
        load_vfs("/nonexistent/path.csv")


def test_load_bad_header(tmp_path):
    """Неверные колонки дают VfsError."""
    path = tmp_path / "bad.csv"
    path.write_text(CSV_BAD_HEADER, encoding="utf-8")
    with pytest.raises(VfsError):
        load_vfs(str(path))


def test_load_bad_type(tmp_path):
    """Неизвестный тип записи даёт VfsError."""
    path = tmp_path / "bad_type.csv"
    path.write_text(CSV_BAD_TYPE, encoding="utf-8")
    with pytest.raises(VfsError):
        load_vfs(str(path))


def test_save_and_load_roundtrip(tmp_path):
    """Сохранить → загрузить → получить то же дерево."""
    vfs = Vfs()
    vfs.add_file("/home/notes.txt", "hello")
    out = tmp_path / "out.csv"
    save_vfs(vfs, str(out))

    loaded = load_vfs(str(out))
    assert loaded.get("/home/notes.txt") is not None
