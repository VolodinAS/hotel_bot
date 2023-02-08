from operator import itemgetter

from loguru import logger
from telebot.types import Message

from database.models import History
from database.models import User
from loader import bot
from loader import bot_config
from utils.misc.parse_hotel_data import parse_hotel_data


def get_hotels_list(
        response_result: list,
        user_data: User,
        new_search: History,
        check_total_days: int,
        message_loading: Message
) -> list:
    """
    Получаем данные отеля из апи
    :param list response_result: данные отелей
    :param User user_data: данные юзера
    :param History new_search: новая запись истории поиска
    :param int check_total_days: количество дней
    :param Message message_loading: данные сообщения
    :return: list
    """
    
    logger.debug('get_hotels_list start')
    current = 1
    hotel_not_sorted = []
    for hotel_data in response_result:
        hotel_parse = parse_hotel_data(hotel_data, user_data, new_search, check_total_days)
        
        if user_data.command == 'bestdeal':
            if hotel_parse['center'] != bot_config.strings.max_dist:
                if hotel_parse['center'] <= user_data.distance:
                    hotel_not_sorted.append(hotel_parse)
            else:
                hotel_not_sorted.append(hotel_parse)
        else:
            hotel_not_sorted.append(hotel_parse)
        current += 1
        percent = round(current / user_data.hotel_numbers * 10000) / 100
        bot.edit_message_text(
            text=f'Информация по отелям в "{user_data.trip_dest_name}" найдена..\nЗагрузка {percent}%...',
            chat_id=message_loading.chat.id,
            message_id=message_loading.message_id
        )

    logger.debug('get_hotels_list end')
    return hotel_not_sorted


def get_sorted_hotels(hotel_not_sorted, user_data: User) -> list:
    """
    Сортировка полученных отелей
    :param list hotel_not_sorted: список отелей
    :param User user_data: данные юзера
    :return: list
    """
    
    if user_data.command == 'bestdeal':
        sort_key = 'center'
        is_asc_not_reverse = False
    else:
        sort_key = 'hotel_price_float'
        if user_data.command == 'highprice':
            is_asc_not_reverse = True
        else:
            is_asc_not_reverse = False
    
    return sorted(hotel_not_sorted, key=itemgetter(sort_key), reverse=is_asc_not_reverse)
