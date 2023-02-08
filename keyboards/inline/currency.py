from telebot import types
from telebot.types import InlineKeyboardMarkup

from config_data.currency import CURRENCIES


def currency_inline_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки валют (при заполнении анкеты в профиле)
    :return: InlineKeyboardMarkup
    """
    
    markup = types.InlineKeyboardMarkup(row_width=3)
    for cur, data in CURRENCIES.items():
        key_currency = types.InlineKeyboardButton(data['title'], callback_data=f'currencies {cur}')
        markup.add(key_currency)

    return markup
