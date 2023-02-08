from loguru import logger
from telebot import types
from telebot.types import InlineKeyboardMarkup

from utils.pretty import pretty


def current_city_buttons(cities_data: list) -> InlineKeyboardMarkup | bool:
    """
    Кнопки выбора точной локации
    :param: dict cities_data
    :return: InlineKeyboardMarkup
    """
    
    if len(cities_data) > 0:
        cities = types.InlineKeyboardMarkup(row_width=1)
        pretty(cities_data)
        for cities_item in cities_data:
            if cities_item['type'] != 'HOTEL':
                city_id = cities_item['gaiaId']
                city_name = cities_item['regionNames']['shortName']
                callback = f'bcc {city_id} {city_name}'
                if len(callback) > 40:
                    callback = callback[0:37] + '...'
                logger.info(callback)
                city_button = types.InlineKeyboardButton(city_name, callback_data=callback)
                cities.add(city_button)
        return cities
    else:
        return False
