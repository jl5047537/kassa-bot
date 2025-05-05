"""
Модуль основных состояний.
Содержит состояния FSM для обработки основных действий.
"""

from aiogram.dispatcher.filters.state import State, StatesGroup

class MainStates(StatesGroup):
    """
    Группа основных состояний.
    """
    # Состояния для регистрации
    waiting_for_phone = State()  # Ожидание номера телефона
    waiting_for_name = State()  # Ожидание имени
    waiting_for_surname = State()  # Ожидание фамилии 