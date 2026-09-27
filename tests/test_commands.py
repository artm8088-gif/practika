"""Тесты логики команд поверх VFS."""

from src.commands import _resolve


def test_resolve_absolute():
    """Абсолютный путь не меняется."""
    assert _resolve("/home/mark", "/tmp") == "/home/mark"


def test_resolve_relative():
    """Относительный путь склеивается с cwd."""
    assert _resolve("mark", "/home") == "/home/mark"


def test_resolve_parent():
    """`..` поднимает на уровень выше."""
    assert _resolve("..", "/home/mark") == "/home"


def test_resolve_current():
    """`.` оставляет тот же путь."""
    assert _resolve(".", "/home/mark") == "/home/mark"
