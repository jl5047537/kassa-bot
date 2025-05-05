"""
Модуль состояний для пользователей.
Содержит состояния FSM для обработки действий пользователей.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class UserStates(StatesGroup):
    """
    Группа состояний для пользователей.
    """
    # Состояния для работы с пользователями
    user_panel = State()  # Состояние пользовательской панели
    waiting_for_user_data = State()  # Ожидание данных для добавления пользователя
    waiting_for_user_remove = State()  # Ожидание данных для удаления пользователя
    waiting_for_user_edit = State()  # Ожидание данных для редактирования пользователя 