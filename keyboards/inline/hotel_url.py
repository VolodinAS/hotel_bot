from telebot import types
from telebot.types import InlineKeyboardMarkup

from loader import bot_config


def hotel_url_inline(hotel_id) -> InlineKeyboardMarkup:
    """
    Кнопка ссылки на сайт отеля
    :param: int hotel_id ид отеля
    :return: InlineKeyboardMarkup
    """
    url = bot_config.rapid_api.hotel_url.format(hotel_id=hotel_id)
    url_inline = types.InlineKeyboardMarkup(row_width=1)
    url_go = types.InlineKeyboardButton(text='Перейти на сайт ➡', url=url)
    url_inline.add(url_go)
    return url_inline
