"""
#### *Модуль обработки ввода в Moon*

---

##### Версия: 1.0.3

*Автор: Павлов Иван (Pavlov Ivan)*

*Лицензия: MIT*
##### Реализованно на 100%

---

✓ Полноценная обработка ввода мыши:
  - Определение позиции (экран/окно)
  - Отслеживание кликов и нажатий
  - Расчет скорости движения

✓ Комплексная работа с клавиатурой:
  - Определение нажатий клавиш
  - Поддержка комбинаций клавиш
  - Отслеживание "кликов" клавиш

✓ Гибкая система событий:
  - Подписка на события ввода
  - Менеджер событий с callback-функциями
  - Фильтрация и обработка событий

✓ Готовые интерфейсы:
  - MouseInterface - предварительно настроенный объект мыши
  - KeyBoardInterface - готовый объект клавиатуры

---

:Requires:

• Python 3.8+

• Библиотека keyboard (для обработки клавиатуры)

• Библиотека ctypes (для работы с DLL)

• Moon.dll (нативная библиотека обработки ввода)

---

== Лицензия MIT ==================================================

[MIT License]
Copyright (c) 2025 Pavlov Ivan

Данная лицензия разрешает лицам, получившим копию данного программного обеспечения
и сопутствующей документации (в дальнейшем именуемыми «Программное Обеспечение»),
безвозмездно использовать Программное Обеспечение без ограничений, включая неограниченное
право на использование, копирование, изменение, слияние, публикацию, распространение,
сублицензирование и/или продажу копий Программного Обеспечения, а также лицам, которым
предоставляется данное Программное Обеспечение, при соблюдении следующих условий:

[ Уведомление об авторском праве и данные условия должны быть включены во все копии ]
[                 или значительные части Программного Обеспечения.                  ]

ПРОГРАММНОЕ ОБЕСПЕЧЕНИЕ ПРЕДОСТАВЛЯЕТСЯ «КАК ЕСТЬ», БЕЗ КАКИХ-ЛИБО ГАРАНТИЙ, ЯВНО
ВЫРАЖЕННЫХ ИЛИ ПОДРАЗУМЕВАЕМЫХ, ВКЛЮЧАЯ, НО НЕ ОГРАНИЧИВАЯСЬ ГАРАНТИЯМИ ТОВАРНОЙ
ПРИГОДНОСТИ, СООТВЕТСТВИЯ ПО ЕГО КОНКРЕТНОМУ НАЗНАЧЕНИЮ И ОТСУТСТВИЯ НАРУШЕНИЙ ПРАВ.
НИ В КАКОМ СЛУЧАЕ АВТОРЫ ИЛИ ПРАВООБЛАДАТЕЛИ НЕ НЕСУТ ОТВЕТСТВЕННОСТИ ПО ИСКАМ О
ВОЗМЕЩЕНИИ УЩЕРБА, УБЫТКОВ ИЛИ ДРУГИХ ТРЕБОВАНИЙ ПО ДЕЙСТВУЮЩЕМУ ПРАВУ ИЛИ ИНОМУ,
ВОЗНИКШИМ ИЗ, ИМЕЮЩИМ ПРИЧИНОЙ ИЛИ СВЯЗАННЫМ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ ИЛИ
ИСПОЛЬЗОВАНИЕМ ПРОГРАММНОГО ОБЕСПЕЧЕНИЯ ИЛИ ИНЫМИ ДЕЙСТВИЯМИ С ПРОГРАММНЫМ ОБЕСПЕЧЕНИЕМ.
"""

import os
import time
import mouse
import ctypes
import keyboard
import win32gui         # pyright: ignore[reportMissingModuleSource]
import win32api         # pyright: ignore[reportMissingModuleSource]
import win32process     # pyright: ignore[reportMissingModuleSource]

from enum import STRICT, Enum
from functools import lru_cache
from threading import Event, Thread
from typing import Any, Callable, Literal, Final, final, Optional, Union, Set, Dict


from Moon.python.Types import AutoIdentifier, Self
from Moon.python.Vectors import Vector2f, Vector2i  # Векторные операции для позиций
from Moon.python.utils import find_library, LibraryLoadError




# ==================== КЛАССЫ ОШИБОК ====================
class InputError(Exception):
    """Базовый класс для всех ошибок модуля ввода"""
    pass

class InvalidInputError(InputError):
    """Некорректные параметры ввода"""
    pass


# Загрузка библиотеки
try:
    _lib = ctypes.CDLL(find_library())
except Exception as e:
    raise LibraryLoadError(f"Failed to load Moon library: {e}")

# Проверка наличия обязательных функций
REQUIRED_FUNCTIONS = [
    '_Keyboard_IsKeyPressed', '_Mouse_IsButtonPressed',
    '_Mouse_GetPositionX', '_Mouse_GetPositionY',
    '_Mouse_GetPositionXWindow', '_Mouse_GetPositionYWindow',
    '_Mouse_SetPosition', '_Mouse_SetPositionWindow'
]

for func in REQUIRED_FUNCTIONS:
    if not hasattr(_lib, func):
        raise LibraryLoadError(f"Required function {func} not found in library")


class KeyboardLayout:
    """Класс для представления раскладки клавиатуры"""
    def __init__(self, name: str, value: int):
        self.__name = name     # Имя раскладки
        self.__value = value   # Значение раскладки (id)

    def get_name(self) -> str:
        """Возвращает имя раскладки"""
        return self.__name

    def get_value(self) -> int:
        """Возвращает значение раскладки"""
        return self.__value

    def __str__(self) -> str:
        """Возвращает строковое представление раскладки"""
        return f"Layout: {self.__name} ({self.__value})"

    def __eq__(self, value: object) -> bool:
        """Сравнивает раскладки"""
        if not isinstance(value, KeyboardLayout):
            return NotImplemented
        return self.__value == value.get_value()

    def __ne__(self, value: object) -> bool:
        """Сравнивает раскладки"""
        if not isinstance(value, KeyboardLayout):
            return NotImplemented
        return self.__value != value.get_value()

    def __hash__(self) -> int:
        """Возвращает хэш-код раскладки"""
        return hash(self.__value)

# Layouts ===========================================================
LAYOUT_EN =       KeyboardLayout("EN", 0x0409)       # English layout
LAYOUT_RU =       KeyboardLayout("RU", 0x0419)       # Russian layout
LAYOUT_UNKNOWN =  KeyboardLayout("Unknown", 0xffff)  # Unknown layout
# ===================================================================


def convert_ru_with_qwerty_layout(key: str) -> str:
    """
    #### Метод для конвертации русских букв в английские с использованием QWERTY раскладки.

    ---

    :Args:
        key (str): Ключ для конвертации.

    :Returns:
        str: Конвертированный символ.

    """
    return Keyboard.QWERTY_LAYOUT[key]


# Метод для получения текущей раскладки клавиатуры на Windows
if os.name == 'nt':
    def get_keyboard_layout() -> KeyboardLayout:
        """
        #### Определяет текущую раскладку клавиатуры активного окна.

        ---

        :Returns:
            str: "RU" для русской раскладки, "EN" для английской,
                или "Unknown" для любой другой.

        ---

        :Note:
            Эта функция специфична для операционной системы Windows,
            так как использует модули `win32gui`, `win32process`, `win32api`.
        """

        hwnd = win32gui.GetForegroundWindow()

        thread_id, _ = win32process.GetWindowThreadProcessId(hwnd)
        layout_id = win32api.GetKeyboardLayout(thread_id)

        lang_id = layout_id & 0xFFFF

        if lang_id == 0x0419: # Russian keyboard layout
            return LAYOUT_RU
        elif lang_id == 0x0409:
            return LAYOUT_EN
        else:
            return LAYOUT_UNKNOWN
# Метод для определения раскладки клавиатуры на Linux
if os.name == 'linux':
    def get_keyboard_layout() -> KeyboardLayout:
        """
        #### Определяет текущую раскладку клавиатуры на Linux.

        ---

        :Returns:
            KeyboardLayout: Текущая раскладка клавиатуры

        ---

        :Raises:
            InputError: Ошибка при определении раскладки
        """
        try:
            with open('/etc/default/keyboard', 'r') as f:
                for line in f:
                    if line.startswith('XKBLAYOUT='):
                        layout = line.split('=')[1].strip().strip('"')
                        if layout == 'ru':
                            return LAYOUT_RU
                        elif layout == 'us':
                            return LAYOUT_EN
                        else:
                            return LAYOUT_UNKNOWN
        except Exception as e:
            raise InputError(f"Error getting keyboard layout: {e}")

def is_key_pressed(key: Union[int, str]) -> bool:
    """
    #### Проверяет нажатие клавиши через нативную библиотеку

    ---

    :Arguments:
        key: Код клавиши (int) или символ (str)

    ---

    :Returns:
        bool: Нажата ли клавиша

    ---

    :Raises:
        InvalidInputError: Некорректный формат клавиши
        InputError: Ошибка при проверке состояния
    """
    # Конвертация строки в код символа
    if isinstance(key, str):
        if len(key) != 1:
            raise InvalidInputError("Key symbol must be a single character")
        key = ord(key)
    elif not isinstance(key, int):
        raise InvalidInputError("Key must be either int (keycode) or str (single character)")

    try:
        # Настройка и вызов нативной функции
        _lib._Keyboard_IsKeyPressed.restype = ctypes.c_bool
        _lib._Keyboard_IsKeyPressed.argtypes = [ctypes.c_int]
        return _lib._Keyboard_IsKeyPressed(key)
    except Exception as e:
        raise InputError(f"Key press check failed: {e}")

def is_mouse_button_pressed(button: int) -> bool:
    """
    #### Проверяет нажатие кнопки мыши

    ---

    :Arguments:
        button: Номер кнопки (0-левая, 1-правая, 2-средняя)

    ---

    :Returns:
        bool: Нажата ли кнопка

    ---

    :Raises:
        InvalidInputError: Некорректный номер кнопки
        InputError: Ошибка при проверке состояния
    """
    if not isinstance(button, int) or button < 0 or button > 2:
        raise InvalidInputError("Mouse button must be integer 0-2")

    try:
        _lib._Mouse_IsButtonPressed.restype = ctypes.c_bool
        _lib._Mouse_IsButtonPressed.argtypes = [ctypes.c_int]
        return _lib._Mouse_IsButtonPressed(button)
    except Exception as e:
        raise InputError(f"Mouse button check failed: {e}")

def get_mouse_position() -> Vector2i:
    """
    #### Получает текущую позицию курсора на экране

    ---

    :Returns:
        Vector2i: Позиция (x, y) в пикселях

    ---

    :Raises:
        InputError: Ошибка при получении позиции
    """
    try:
        _lib._Mouse_GetPositionX.restype = ctypes.c_int
        _lib._Mouse_GetPositionY.restype = ctypes.c_int
        return Vector2i(_lib._Mouse_GetPositionX(), _lib._Mouse_GetPositionY())
    except Exception as e:
        raise InputError(f"Failed to get mouse position: {e}")

def get_mouse_position_in_window(window: Any) -> Vector2i:
    """
    #### Получает позицию курсора относительно окна

    ---

    :Arguments:
        window: Объект окна с методом get_ptr()

    ---

    :Returns:
        Vector2i: Позиция (x, y) относительно окна

    ---

    :Raises:
        InvalidInputError: Некорректный объект окна
        InputError: Ошибка при получении позиции
    """
    if not hasattr(window, 'get_ptr'):
        raise InvalidInputError("Window object must have get_ptr() method")

    try:
        window_ptr = window.get_ptr()
        if not isinstance(window_ptr, int):
            raise InvalidInputError("Window pointer must be integer")

        _lib._Mouse_GetPositionXWindow.restype = ctypes.c_int
        _lib._Mouse_GetPositionYWindow.restype = ctypes.c_int
        _lib._Mouse_GetPositionXWindow.argtypes = [ctypes.c_void_p]
        _lib._Mouse_GetPositionYWindow.argtypes = [ctypes.c_void_p]

        x = _lib._Mouse_GetPositionXWindow(window_ptr)
        y = _lib._Mouse_GetPositionYWindow(window_ptr)
        return Vector2i(x, y)
    except Exception as e:
        raise InputError(f"Failed to get window mouse position: {e}")

def set_mouse_position(position: Vector2i | Vector2f) -> None:
    """
    #### Устанавливает позицию курсора мыши на экране

    ---

    :Arguments:
        position: Vector2i - Позиция (x, y) в глобальных координатах экрана

    ---

    :Raises:
        InputError: Ошибка при установке позиции мыши

    :Note:
        Позиция устанавливается в глобальных координатах экрана,
        а не относительно какого-либо окна
    """
    try:
        _lib._Mouse_SetPosition.argtypes = [ctypes.c_int, ctypes.c_int]
        _lib._Mouse_SetPosition(int(position.x), int(position.y))
    except Exception as e:
        raise InputError(f"Failed to set mouse position: {e}")

def set_mouse_position_in_window(window: Any, position: Vector2i | Vector2f) -> None:
    """
    #### Устанавливает позицию курсора мыши относительно окна

    ---

    :Arguments:
        window: Any - Объект окна с методом get_ptr()
        position: Vector2i - Позиция (x, y) относительно окна

    ---

    :Raises:
        InvalidInputError: Некорректный объект окна или указатель
        InputError: Ошибка при установке позиции мыши

    :Note:
        Позиция устанавливается относительно левого верхнего угла окна.
        Для работы функции объект окна должен иметь метод get_ptr(),
        возвращающий указатель на sf::RenderWindow
    """

    if not hasattr(window, 'get_ptr'):
        raise InvalidInputError("Window object must have get_ptr() method")

    window_ptr = window.get_ptr()
    if not isinstance(window_ptr, int):
        raise InvalidInputError("Window pointer must be integer")

    _lib._Mouse_SetPositionWindow.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
    _lib._Mouse_SetPositionWindow(int(position.x), int(position.y), window_ptr)


@final
class MouseButtons(Enum):
    """Перечисление кнопок мыши"""
    LEFT = 0    # Левая кнопка
    RIGHT = 1   # Правая кнопка
    MIDDLE = 2  # Средняя кнопка (колесо)


def convert_mouse_button(button: Union[Literal["left", "right", "middle"], MouseButtons]) -> int:
    """
    #### Конвертирует кнопку мыши в числовой код

    ---

    :Arguments:
        button: Название кнопки или элемент MouseButtons

    ---

    :Returns:
        int: Числовой код кнопки

    ---

    :Raises:
        InvalidInputError: Некорректное название кнопки
    """
    if isinstance(button, MouseButtons):
        return button.value
    elif isinstance(button, str):
        button_str = button.lower()
        if button_str == "left": return 0
        elif button_str == "right": return 1
        elif button_str == "middle": return 2

    raise InvalidInputError(
        f"Invalid mouse button: {button}. Expected 'left', 'right', 'middle' or MouseButtons enum"
    )

@final
class Mouse:
    """
    Основной класс для работы с мышью

    Предоставляет:
    - Проверку нажатий кнопок
    - Отслеживание кликов
    - Получение позиции курсора
    - Расчет скорости движения
    - Перемещение мыши
    - Установка координат
    - Одиночный клик
    - Двойной клик
    """

    Buttons = MouseButtons  # Доступ к перечислению кнопок

    def __init__(self):
        """Инициализация состояния мыши"""
        self._last_click_state = {
            "left": False,   # Состояние левой кнопки в предыдущем кадре
            "right": False, # Состояние правой кнопки
            "middle": False # Состояние средней кнопки
        }
        self._last_position = get_mouse_position()  # Позиция в предыдущем кадре

    @classmethod
    def get_press(cls, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, нажата ли кнопка мыши в текущий момент

        ---

        :Arguments:
            button: Кнопка для проверки

        ---

        :Returns:
            bool: Нажата ли кнопка
        """
        return is_mouse_button_pressed(convert_mouse_button(button))

    @classmethod
    def in_window(cls, window: Any) -> bool:
        """
        Проверяет, находится ли курсор мыши внутри окна

        ---

        :Arguments:
            window: Окно для проверки

        ---

        :Returns:
            bool: Внутри ли окна
        """
        mouse_position = cls.get_position()
        window_pos = window.get_position()
        window_size = window.get_size()

        if (window_pos.x <= mouse_position.x <= window_pos.x + window_size.x and
            window_pos.y <= mouse_position.y <= window_pos.y + window_size.y + 31):
            return True
        return False

    def get_click(self, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, была ли кнопка только что нажата (в этом кадре)

        ---

        :Arguments:
            button: Кнопка для проверки

        ---

        :Returns:
            bool: Был ли клик

        ---

        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(button)
            button_name = button if isinstance(button, str) else button.name.lower()

            # Если кнопка нажата сейчас, но не была нажата в прошлом кадре
            if current_state and not self._last_click_state[button_name]:
                self._last_click_state[button_name] = True
                return True
            elif not current_state:
                self._last_click_state[button_name] = False
            return False
        except Exception as e:
            raise InputError(f"Failed to get mouse click: {e}")

    def get_release(self, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> bool:
        """
        #### Проверяет, была ли кнопка только что отпущена

        ---

        :Arguments:
            button: Кнопка для проверки

        ---

        :Returns:
            bool: Был ли отпуск

        ---

        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(button)
            button_name = button if isinstance(button, str) else button.name.lower()

            # Если кнопка не нажата сейчас, но была нажата в прошлом кадре
            if not current_state and self._last_click_state[button_name]:
                self._last_click_state[button_name] = False
                return True
            elif current_state:
                self._last_click_state[button_name] = True
            return False
        except Exception as e:
            raise InputError(f"Failed to get mouse release: {e}")

    @classmethod
    def get_position_in_window(cls, window: Any) -> Vector2i:
        """
        #### Получает позицию курсора относительно окна

        ---

        :Arguments:
            window: Объект окна

        ---

        :Returns:
            Vector2i: Позиция относительно окна
        """
        return get_mouse_position_in_window(window)

    def get_speed(self) -> Vector2i:
        """
        #### Рассчитывает скорость движения мыши (пикселей/кадр)

        ---

        :Returns:
            Vector2i: Вектор скорости (dx, dy)

        ---

        :Raises:
            InputError: Ошибка при расчете скорости
        """
        try:
            current_pos = get_mouse_position()
            speed = current_pos - self._last_position
            self._last_position = current_pos
            return speed
        except Exception as e:
            raise InputError(f"Failed to calculate mouse speed: {e}")

    @classmethod
    def get_position(cls) -> Vector2i:
        """
        #### Получает абсолютную позицию курсора на экране

        ---

        :Returns:
            Vector2i: Позиция (x, y)
        """
        return get_mouse_position()

    @classmethod
    def set_position(cls, position: Vector2i | Vector2f) -> None:
        """
        #### Устанавливает абсолютную позицию курсора на экране

        :Args:
            position (Vector2i | Vector2f): Новая позиция курсора

        :Raises:
            InputError: Если не удалось установить позицию курсора
        """
        set_mouse_position(position)

    @classmethod
    def set_position_in_window(cls, window: Any,  position: Vector2i | Vector2f) -> None:
        """
        #### Устанавливает абсолютную позицию курсора в окне

        :Args:
            position (Vector2i | Vector2f): Новая позиция курсора

        :Raises:
            InputError: Если не удалось установить позицию курсора
        """
        set_mouse_position_in_window(window, position)

    @classmethod
    def click(cls, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> None:
        mouse.click(str(button))

    @classmethod
    def double_click(cls, button: Union[Literal["left", "right", "middle"], MouseButtons]) -> None:
        mouse.double_click(str(button))

    @classmethod
    def move(cls, position: Vector2i | Vector2f, duration: float | int = 0) -> None:
        """
        Перемещает курсор в указанную позицию с заданным временем перемещения.

        :Args:
            position (Vector2i | Vector2f): Новая позиция курсора
            duration (float | int): Время перемещения в секундах или миллисекундах

        :Raises:
            InputError: Если не удалось переместить курсор

        :Warning:
            Если время перемещения слишком короткое, курсор может не успеть переместиться до окончания выполнения программы.
            Метод блокирует поток до окончания перемещения. (рекомендуется использовать в другом потоке, для того чтобы не блокировать основной поток)
        """
        mouse.move(position.x, position.y, True, duration) # pyright: ignore

    @classmethod
    def _move_thread(cls, position: Vector2i | Vector2f, duration: float | int):
        mouse.move(position.x, position.y, True, duration) # pyright: ignore

    @classmethod
    def daemon_move(cls, position: Vector2i | Vector2f, duration: float | int):
        """
        #### Демонизированный метод для перемещения курсора

        ---

        :Logic:
            1. Создается новый поток, который вызывает метод _move_thread с переданными параметрами.
            2. Метод _move_thread перемещает курсор на заданную позицию с заданным временем.
            3. После завершения работы метода _move_thread, поток завершается.

        :Warning:
            Этот метод не блокирует поток, а создает новый поток для перемещения курсора.
            Если несколько раз подряд будет создаваться нвоый поток то курсор будет перемещаться не коррктно
            пытаясь успеть за логикой перемещения каждого потока.

        :Args:
            - position: Vector2i | Vector2f - Позиция, на которую нужно переместить курсор.
            - duration: float | int - Время, за которое нужно переместить курсор.

        :Returns:
            None

        :Raises:
            None

        :Example:
            ```py
             Mouse.daemon_move(Vector2i(100, 100), 1)
             Mouse.daemon_move(Vector2f(100.0, 100.0), 1)
            ```


        """
        Thread(target=cls._move_thread, args=(position, duration)).start()



# ////////////////////////////////////////////////////////////////////////////
# Глобальный экземпляр интерфейса мыши
# Используется для удобства, чтобы не создавать экземпляр класса каждый раз
MouseInterface: Final[Mouse] = Mouse()
# ////////////////////////////////////////////////////////////////////////////


@final
class Keyboard:
    """
    Оптимизированный класс для работы с клавиатурой

    Предоставляет:
    - Проверку нажатий клавиш
    - Отслеживание кликов клавиш
    - Работу с комбинациями клавиш
    """

    # Поддерживаемые клавиши с быстрым доступом
    KEYS_ARRAY: Final[list[str]] = [

        # Специальные клавиши
        "esc", "enter", "space", "backspace", "tab", "capslock",
        "shift", "ctrl", "alt", "win", "menu", "pause",

        # Буквы
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л",
        "м", "н", "о", "п", "р", "с", "т", "у", "ф", "х", "ц", "ч", "ш",
        "щ", "ъ", "ы", "ь", "э", "ю", "я",

        # Цифры
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        # Функциональные клавиши
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        # Клавиши управления
        "up", "down", "left", "right",

        # Символы
        "!", "@", "#", "$", "%", "^", "&", "*", "(", ")", "_", "+", "=", "-"
        "`", "~", "{", "}", "[", "]", "|", ":", "\"", "<", ">", "?", "/", ".", ","
    ]

    QWERTY_LAYOUT: Final[dict[str, str]] = {
        "q": "й",
        "w": "ц",
        "e": "у",
        "r": "к",
        "t": "е",
        "y": "н",
        "u": "г",
        "i": "ш",
        "o": "щ",
        "p": "з",
        "a": "ф",
        "s": "ы",
        "d": "в",
        "f": "а",
        "g": "п",
        "h": "р",
        "j": "о",
        "k": "л",
        "l": "д",
        "z": "я",
        "x": "ч",
        "c": "с",
        "v": "м",
        "b": "и",
        "n": "т",
        "m": "ь",
        "[": "х",
        "]": "ъ",
        "'": "э",
    }

    CHAR_SET: Final[str] = "qwertyuiopasdfghjklzxcvbnmёйцукенгшщзхфывапролджэячсмитьбю"

    # Кэш для быстрого доступа к нормализованным комбинациям
    _COMBINATION_CACHE: Dict[str, Set[str]] = {}
    _PRESSED_KEYS_CACHE: Set[str] = set()
    _LAST_UPDATE_TIME: float = 0
    _CACHE_TTL: float = 0.05 # кэширование

    def __init__(self):
        """Инициализация состояния клавиатуры"""
        self._last_click_state: Dict[str, bool] = {}
        self._last_pressed_keys: Set[str] = set()
        self._last_combination_state: Dict[str, bool] = {}

    @classmethod
    def _key_in_qwerty_layout(cls, key: str) -> bool:
        return key in cls.QWERTY_LAYOUT.keys()

    @classmethod
    def _update_pressed_cache(cls) -> None:
        """
        #### Обновляет кэш нажатых клавиш с ограничением по времени

        ---

        :Raises:
            InputError: Ошибка при обновлении кэша
        """
        current_time = time.time()

        if current_time - cls._LAST_UPDATE_TIME > cls._CACHE_TTL:
            cls._PRESSED_KEYS_CACHE.clear()
            for key in cls.KEYS_ARRAY:
                try:
                    if keyboard.is_pressed(key):
                        if get_keyboard_layout() == LAYOUT_RU:

                            if cls._key_in_qwerty_layout(key):
                                key = cls.QWERTY_LAYOUT[key]

                        cls._PRESSED_KEYS_CACHE.add(key)
                except: ...
            cls._LAST_UPDATE_TIME = current_time


    @classmethod
    def get_press(cls, keys: str) -> bool:
        """
        #### Проверяет, нажата ли клавиша/комбинация (оптимизированная версия)

        ---

        :Arguments:
            keys: Клавиша или комбинация (например "ctrl+c")

        ---

        :Returns:
            bool: Нажата ли клавиша

        ---

        :Raises:
            InvalidInputError: Некорректный формат клавиши
            InputError: Ошибка при проверке состояния
        """
        if not isinstance(keys, str):
            raise InvalidInputError("Keys must be a string")

        # Для одиночных клавиш используем быструю проверку
        if '+' not in keys:
            cls._update_pressed_cache()
            return keys.lower() in cls._PRESSED_KEYS_CACHE

        # Для комбинаций используем оптимизированный метод
        return cls.get_press_combination(keys)

    def get_press_any(self) -> bool:
        """
        #### Проверяет, нажата ли хотя бы одна клавиша

        ---

        :Returns:
            bool: Нажата ли хотя бы одна клавиша
        """
        press_array = [self.get_press(key) for key in self.KEYS_ARRAY]
        return any(press_array)

    def get_click_any(self) -> bool:
        """
        #### Проверяет, была ли хотя бы одна клавиша только что нажата

        ---

        :Returns:
            bool: Была ли нажата хотя бы одна клавиша
        """
        click_array = [self.get_click(key) for key in self.KEYS_ARRAY]
        return any(click_array)


    def get_click(self, keys: str) -> bool:
        """
        #### Проверяет, была ли клавиша только что нажата (оптимизированная версия)

        ---

        :Arguments:
            keys: Клавиша для проверки

        ---

        :Returns:
            bool: Был ли клик

        ---

        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press(keys)

            # Быстрая проверка состояния через локальный кэш
            was_pressed = self._last_click_state.get(keys, False)

            if current_state and not was_pressed:
                self._last_click_state[keys] = True
                return True
            elif not current_state:
                self._last_click_state[keys] = False

            return False
        except Exception as e:
            raise InputError(f"Failed to get key click: {e}")

    @classmethod
    @lru_cache(maxsize=128)
    def _normalize_combination(cls, keys: str) -> Set[str]:
        """
        #### Нормализует и кэширует комбинацию клавиш

        ---

        :Arguments:
            keys: Комбинация клавиш для нормализации

        ---

        :Returns:
            Set[str]: Нормализованное множество клавиш
        """
        return set(key.strip().lower() for key in keys.split('+'))

    @classmethod
    def get_press_combination(cls, keys: str) -> bool:
        """
        #### Оптимизированная проверка комбинации клавиш

        ---

        :Arguments:
            keys: Комбинация клавиш через "+" (например "ctrl+shift+c")

        ---

        :Returns:
            bool: Нажата ли комбинация

        ---

        :Raises:
            InvalidInputError: Некорректный формат комбинации
            InputError: Ошибка при проверке состояния
        """
        if not isinstance(keys, str) or '+' not in keys:
            raise InvalidInputError("Key combination must be string with '+' separator")

        try:
            # Используем кэшированную нормализацию
            keys_set = cls._normalize_combination(keys)

            # Обновляем кэш нажатых клавиш
            cls._update_pressed_cache()

            # Быстрая проверка подмножества
            return keys_set.issubset(cls._PRESSED_KEYS_CACHE)
        except Exception as e:
            raise InputError(f"Failed to check key combination: {e}")

    def get_click_combination(self, keys: str) -> bool:
        """
        #### Проверяет, была ли комбинация только что нажата (оптимизированная версия)

        ---

        :Arguments:
            keys: Комбинация клавиш

        ---

        :Returns:
            bool: Была ли нажата комбинация

        ---

        :Raises:
            InputError: Ошибка при проверке состояния
        """
        try:
            current_state = self.get_press_combination(keys)
            was_pressed = self._last_combination_state.get(keys, False)

            if current_state and not was_pressed:
                self._last_combination_state[keys] = True
                return True
            elif not current_state:
                self._last_combination_state[keys] = False

            return False
        except Exception as e:
            raise InputError(f"Failed to get combination click: {e}")

    @classmethod
    def get_pressed_keys(cls) -> list[str]:
        """
        #### Оптимизированное получение списка нажатых клавиш

        ---

        :Returns:
            list[str]: Список нажатых клавиш

        ---

        :Raises:
            InputError: Ошибка при получении состояния
        """
        cls._update_pressed_cache()
        return list(cls._PRESSED_KEYS_CACHE)

    def update_frame(self) -> None:
        """
        #### Метод для обновления состояния в конце кадра
        (опционально, для ручного управления кэшем)
        """
        self._update_pressed_cache()

    def clear_cache(self) -> None:
        """
        #### Очищает внутренние кэши
        """
        self._last_click_state.clear()
        self._last_combination_state.clear()
        self._normalize_combination.cache_clear()
        self._PRESSED_KEYS_CACHE.clear()

# ////////////////////////////////////////////////////////////////////////////
# Глобальный экземпляр интерфейса клавиатуры
# Используется для удобства, чтобы не создавать экземпляр класса каждый раз
KeyBoardInterface: Final[Keyboard] = Keyboard()
# ////////////////////////////////////////////////////////////////////////////

class Listener:
    class ObjectType(Enum):
        MOUSE = "mouse"
        KEYBOARD = "keyboard"

    class EventType(Enum):
        CLICK = "click"
        PRESS = "press"

    def __init__(self, obj: ObjectType, event: EventType, id: str | int | None = None) -> None:
        self.__obj: Mouse | Keyboard | None = Mouse() if obj == Listener.ObjectType.MOUSE else Keyboard() \
                                                      if obj == Listener.ObjectType.KEYBOARD else None

        self.__event: Listener.EventType = event
        self.__id: str | int = AutoIdentifier() if id is None else id

    def get_id(self) -> str | int:
        return self.__id

    def get_object(self) -> Mouse | Keyboard | None:
        return self.__obj

    def get_event(self) -> EventType:
        return self.__event

    def __str__(self) -> str:
        return f'Listener: obj({self.__obj.__class__.__name__}), event({self.__event.name}), id = {self.__id}'

class ListenersManager:
    def __init__(self) -> None:
        self.__listeners: list[Listener] = []
        self.__event_results: dict[str, bool] = {}
