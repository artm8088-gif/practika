"""Основная логика REPL: разбор, диспетчеризация и обработка ошибок."""

from collections.abc import Callable

from .commands import cmd_cd, cmd_exit, cmd_ls

# Имя команды -> обработчик. Использование словаря делает логику
# диспетчеризации плоской и снижает цикломатическую сложность.
COMMANDS: dict[str, Callable[[list[str]], str]] = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}

# Шаблон сообщения об неизвестной команде
UNKNOWN_COMMAND_TEMPLATE = "shell: command not found: {name}"


def parse_input(raw: str) -> tuple[str, list[str]]:
    """Разбирает ввод пользователя на имя команды и список аргументов.

    Пустой ввод возвращает пустое имя команды, которое вызывающая
    сторона должна рассматривать как отсутствие действия.
    """
    parts = raw.strip().split()
    if not parts:
        return "", []
    return parts[0], parts[1:]


def is_exit(command: str) -> bool:
    """Возвращает True, если данная команда запрашивает завершение оболочки."""
    return command == "exit"


def execute(raw: str) -> str:
    """Разбирает и диспетчеризует одну строку пользовательского ввода.

    Возвращает текстовый результат, который должен быть показан в консоли.
    Неизвестные команды порождают сообщение об ошибке в стиле UNIX.
    """
    command, args = parse_input(raw)

    if not command:
        return ""

    handler = COMMANDS.get(command)
    if handler is None:
        return UNKNOWN_COMMAND_TEMPLATE.format(name=command)

    return handler(args)
