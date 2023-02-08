from telebot import types
from telebot.types import InlineKeyboardMarkup


def profile_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопка настроек профиля
    :return: InlineKeyboardMarkup
    """
    markup = types.InlineKeyboardMarkup(row_width=1)
    key_repeat = types.InlineKeyboardButton("Заполнить заново", callback_data='repeat')
    key_clear = types.InlineKeyboardButton("Очистить историю поиска", callback_data='clear_history')
    markup.add(key_repeat, key_clear)
    return markup
