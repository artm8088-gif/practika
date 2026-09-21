"""Точка входа для эмулятора оболочки с графическим интерфейсом."""

import getpass
import socket

import customtkinter as ctk

from src.shell import execute, is_exit

# Шаблон заголовка окна с именем пользователя и именем хоста
WINDOW_TITLE_TEMPLATE = "Shell Emulator - [{user}@{host}]"
# Размер окна
WINDOW_SIZE = "900x600"
# Шаблон приглашения командной строки
PROMPT_TEMPLATE = "{user}@{host}:~$ "
# шрифты
FONT_FAMILY = "JetBrains Mono"
# Размер шрифта
FONT_SIZE = 14
# Отступы
PADDING = 10


def build_title() -> str:
    """Формирует заголовок окна на основе данных пользователя и хоста ОС."""
    user = getpass.getuser()  # Получаем имя текущего пользователя
    host = socket.gethostname()  # Получаем имя хоста
    return WINDOW_TITLE_TEMPLATE.format(user=user, host=host)


def build_prompt() -> str:
    """Формирует строку приглашения, отображаемую перед вводом пользователя."""
    user = getpass.getuser()  # Получаем имя текущего пользователя
    host = socket.gethostname()  # Получаем имя хоста
    return PROMPT_TEMPLATE.format(user=user, host=host)


class ShellApp(ctk.CTk):
    """Главное окно приложения, содержащее интерфейс эмулятора терминала."""

    def __init__(self) -> None:
        super().__init__()
        self.title(build_title())  # Устанавливаем заголовок окна
        self.geometry(WINDOW_SIZE)  # Устанавливаем размер окна
        self.prompt = build_prompt()  # Сохраняем строку приглашения
        self._build_widgets()  # Создаём виджеты

    def _build_widgets(self) -> None:
        """Создаёт и размещает все виджеты графического интерфейса."""
        ctk.set_appearance_mode("dark")  # Устанавливаем тёмную тему
        ctk.set_default_color_theme("blue")  # Устанавливаем синюю цветовую схему

        # Текстовое поле для вывода результатов команд
        self.output = ctk.CTkTextbox(
            self,
            font=(FONT_FAMILY, FONT_SIZE),
            wrap="word",
        )
        self.output.pack(fill="both", expand=True, padx=PADDING, pady=(PADDING, 0))
        self.output.configure(state="disabled")  # Делаем поле только для чтения

        # Поле ввода команд
        self.entry = ctk.CTkEntry(
            self,
            font=(FONT_FAMILY, FONT_SIZE),
            placeholder_text="Type a command and press Enter (try: ls, cd, exit)",
        )
        self.entry.pack(fill="x", padx=PADDING, pady=PADDING)
        self.entry.bind("<Return>", self._on_submit)  # Привязываем обработчик Enter
        self.entry.focus_set()  # Устанавливаем фокус на поле ввода

        self._append(self.prompt)  # Выводим приглашение при запуске

    def _append(self, text: str) -> None:
        """Добавляет текст в область вывода, сохраняя её доступной только для чтения."""
        self.output.configure(state="normal")  # Временно разрешаем редактирование
        self.output.insert("end", text)  # Вставляем текст в конец
        self.output.see("end")  # Прокручиваем к последней строке
        self.output.configure(state="disabled")  # Снова запрещаем редактирование

    def _on_submit(self, _event) -> None:
        """Обрабатывает нажатие Enter: читает ввод, выполняет команду, выводит результат."""
        raw = self.entry.get()  # Получаем введённый текст
        self.entry.delete(0, "end")  # Очищаем поле ввода

        self._append(raw + "\n")  # Отображаем введённую команду

        # Проверяем, является ли команда выходом (exit)
        if is_exit(raw.strip().split()[0] if raw.strip() else ""):
            self._append(execute(raw) + "\n")  # Выполняем команду выхода
            self.after(300, self.destroy)  # Закрываем окно через 300 мс
            return

        result = execute(raw)  # Выполняем команду
        if result:
            self._append(result + "\n")  # Выводим результат, если он есть
        self._append(self.prompt)  # Выводим приглашение для следующей команды


def main() -> None:
    """Запускает эмулятор оболочки с графическим интерфейсом."""
    app = ShellApp()  # Создаём приложение
    app.mainloop()  # Запускаем главный цикл обработки событий


if __name__ == "__main__":
    main()
