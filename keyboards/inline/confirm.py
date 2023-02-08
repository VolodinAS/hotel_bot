from telebot import types
from telebot.types import InlineKeyboardMarkup


def confirm_trip_inline(command: str) -> InlineKeyboardMarkup:
    """
    Кнопка подтверждения поиска
    :param: str command команда
    :return: InlineKeyboardMarkup
    """
    
    confirm = types.InlineKeyboardMarkup(row_width=1)
    confirm_button = types.InlineKeyboardButton('Подтвердить', callback_data=f'confirm_trip {command}')
    
    confirm.add(confirm_button)
    
    return confirm
