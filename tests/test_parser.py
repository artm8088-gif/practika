"""Тесты разбора пользовательского ввода."""

from src.shell import parse_input


def test_parse_command_only():
    """Команда без аргументов."""
    assert parse_input("ls") == ("ls", [])


def test_parse_with_args():
    """Команда с аргументами."""
    assert parse_input("mv a.txt b.txt") == ("mv", ["a.txt", "b.txt"])


def test_parse_empty():
    """Пустая строка."""
    assert parse_input("   ") == ("", [])
