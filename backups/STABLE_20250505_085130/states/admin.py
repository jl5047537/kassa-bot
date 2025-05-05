"""
Модуль состояний администратора.
Содержит состояния для работы с административной панелью.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class AdminStates(StatesGroup):
    """
    Состояния для работы с административной панелью.
    """
    admin_panel = State()  # Основное состояние админ-панели
    waiting_for_admin_id = State()  # Ожидание ввода ID нового администратора
    waiting_for_admin_remove = State()  # Ожидание выбора администратора для удаления
    waiting_for_level_edit = State()  # Ожидание выбора уровня для редактирования
    waiting_for_level_data = State()  # Ожидание ввода данных для уровня 