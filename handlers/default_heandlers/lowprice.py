import json
import math
import os
from datetime import date
from time import sleep

from loguru import logger
from telebot import types
from telebot.types import CallbackQuery
from telebot.types import Message
from telegram_bot_calendar import DetailedTelegramCalendar

from api.api_request import api_request
from api.prepare_request import prepare_request
from database.db_history import add_new_history
from database.db_user import reset_search
from database.models import History
from database.models import User
from handlers.default_heandlers.error import bot_error
from keyboards.inline.confirm import confirm_trip_inline
from keyboards.inline.current_city import current_city_buttons
from keyboards.inline.hotel_url import hotel_url_inline
from keyboards.reply.cancel import cancel_button
from keyboards.reply.cancel import cancel_decorator
from keyboards.reply.cancel import get_instance_message
from keyboards.reply.cancel import go_cancel
from loader import bot
from loader import bot_config
from states.bestdeal_states import BestDealState
from states.lowprice_states import LowPriceState
from utils.check_user import autocheck_user
from utils.check_user import check_user_decorator
from utils.date_and_unix import date_to_unix
from utils.date_and_unix import unix_to_date
from utils.date_and_unix import unix_to_dict
from utils.misc.calendar import MyStyleCalendar
from utils.misc.get_result_by_keys import get_result_by_keys
from utils.misc.sorting_hotels import get_hotels_list
from utils.misc.sorting_hotels import get_sorted_hotels
from utils.pretty import pretty


def _get_payload_for_request(user_data: User) -> dict:
    """
    Формируем параметры запроса
    :param User user_data: данные пользователя
    :return: dict
    """
    sort_order = bot_config.requester.sort
    if user_data.command == 'bestdeal':
        sort_order = bot_config.requester.sort_best
    
    payload = {
        'currency': user_data.currency,
        'eapid': bot_config.requester.default_payload_eapid,
        'locale': bot_config.requester.locale,
        'siteId': bot_config.requester.default_payload_siteId,
        'destination': {
            'regionId': str(user_data.trip_dest_id)
        },
        'checkInDate': unix_to_dict(unix_to_date(user_data.trip_check_in)),
        'checkOutDate': unix_to_dict(unix_to_date(user_data.trip_check_out)),
        'rooms': bot_config.requester.default_payload_rooms,
        'resultsStartingIndex': bot_config.requester.default_payload_resultsStartingIndex,
        'resultsSize': user_data.hotel_numbers,
        'sort': sort_order,
        'filters': bot_config.requester.default_payload_filters
    }
    
    if user_data.command == 'bestdeal':
        payload['sort'] = bot_config.requester.sort_best
        payload['filters']['price'] = {
            "max": user_data.price_max,
            "min": user_data.price_min
        }
    
    return payload


@bot.message_handler(commands=('lg',))
def get_lowprice_results(callback: CallbackQuery, user_data: User = None) -> None:
    """
    Выдача результатов в телеграм
    :param CallbackQuery callback: колбэк
    :param User user_data: юзер
    :return: None
    """
    
    instance = get_instance_message(callback)
    message = instance
    if user_data is not None:
        bot.edit_message_reply_markup(message.chat.id, message.message_id)
        bot.delete_state(chat_id=message.chat.id, user_id=message.from_user.id)
    else:
        user_data = autocheck_user(message.from_user)
        if user_data['result'] is True:
            user_data: User = user_data['user']
        else:
            logger.error('ПОЛЬЗОВАТЕЛЬ НЕ НАЙДЕН')
            logger.debug(user_data)
    
    empty_keyboard = types.ReplyKeyboardRemove()
    message_start = bot.send_message(
        message.chat.id,
        f'Приступаю к загрузке информации по отелям в месте назначения "{user_data.trip_dest_name}"...',
        reply_markup=empty_keyboard
    )
    
    payload = _get_payload_for_request(user_data)
    
    response = prepare_request(payload, user_data, message_start)
    
    response_result = get_result_by_keys(response)
    
    if len(response_result) > 0:
        
        new_search: History = add_new_history(user_data)
        message_loading = bot.send_message(
            chat_id=message_start.chat.id,
            text=f'Информация по отелям в "{user_data.trip_dest_name}" найдена.. Загрузка 0%...'
        )

        bot.delete_message(
            message_start.chat.id,
            message_start.message_id
        )
        
        check_total_sec = user_data.trip_check_out - user_data.trip_check_in
        check_total_days = math.ceil(check_total_sec / 86400) + 1
        
        hotel_not_sorted = get_hotels_list(response_result, user_data, new_search, check_total_days, message_loading)
        
        hotel_sorted = get_sorted_hotels(hotel_not_sorted, user_data)
        
        for hotel_parse in hotel_sorted:
            # Начинаем спамить отели в чат пользователю
            
            if len(hotel_parse['hotel_media']) > 0:
                bot.send_media_group(chat_id=message.chat.id, media=hotel_parse['hotel_media'])
            else:
                if user_data.numbers_of_photo > 0:
                    bot.send_message(
                        chat_id=message_start.chat.id,
                        text='Фотографии не найдены',
                        parse_mode='HTML'
                    )
            sleep(1)
            url_hotel = hotel_url_inline(hotel_parse.get('hotel_id'))
            
            bot.send_message(
                chat_id=message_start.chat.id,
                text=hotel_parse.get('text'),
                parse_mode='HTML',
                reply_markup=url_hotel
            )
            sleep(1)
            # break
        bot.send_message(
            text='✅ Вывод результатов окончен!',
            chat_id=message.chat.id
        )
    else:
        bot.edit_message_text(
            text=f'В "{user_data.trip_dest_name}" нет отелей со свободными местами!',
            chat_id=message_start.chat.id,
            message_id=message_start.id
        )


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'confirm_trip')
@check_user_decorator
def confirmation(callback, user_data: User) -> None:
    """
    Общий хендлер confirmation
    Нужен для тестовой части, когда не хочется каждый раз вводить данные поиска, а просто прописать команду /lg
    :param CallbackQuery callback: колбэк
    :param User user_data: юзер
    :return: None
    """
    
    get_lowprice_results(callback, user_data)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
@cancel_decorator
@check_user_decorator
def get_check_out(callback, user_data: User) -> None:
    """
    Стейт календаря даты check out c разветвлением стейтов в зависимости от команды на bestdeal и остальные
    :param CallbackQuery callback: колбэк
    :param User user_data: юзер
    :return: None
    """
    
    min_date = date.fromtimestamp(user_data.trip_check_in)
    
    result, key, step = MyStyleCalendar(calendar_id=2, min_date=min_date, locale='ru').process(callback.data)
    if not result and key:
        bot.edit_message_text(
            f"Выберите {bot_config.calendar.locale[step]}",
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=key
        )
    
    elif result:
        bot.edit_message_text(
            f"Дата выбытия: <{result}>",
            callback.message.chat.id,
            callback.message.message_id
        )
        
        user_data.trip_check_out = int(date_to_unix(f'{result}'))
        user_data.save()
        
        if user_data.trip_check_in > user_data.trip_check_out:
            bot.send_message(
                f"Дата прибытия не может быть больше даты прибытия! Выберите другую дату",
                callback.message.chat.id,
                callback.message.message_id,
                reply_markup=key
            )
        else:
            
            if user_data.command == 'bestdeal':
                bot.send_message(callback.message.chat.id, f'Укажите минимально искомую цену (в {user_data.currency}):')
                bot.set_state(
                    user_id=callback.message.chat.id,
                    chat_id=callback.message.chat.id,
                    state=BestDealState.price_min,
                )
            else:
                confirm_me = confirm_trip_inline(user_data.command)
                text = f'' \
                       f'Подтвердите поиск:' \
                       f'\n\nВыбранный город: {user_data.trip_dest_name}' \
                       f'\n\nДата прибытия: {unix_to_date(user_data.trip_check_in)}' \
                       f'\n\nДата выбытия: {unix_to_date(user_data.trip_check_out)}' \
                       f'\n\nКоличество отелей: {user_data.hotel_numbers}' \
                       f'\n\nКоличество фото: {user_data.numbers_of_photo}'
                
                bot.send_message(
                    callback.message.chat.id,
                    text,
                    reply_markup=confirm_me
                )


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
@cancel_decorator
@check_user_decorator
def get_check_in(callback: CallbackQuery, user_data: User) -> None:
    """
    Стейт календаря даты check in c переходом на стейт календаря даты check out
    :param CallbackQuery callback: колбэк
    :param User user_data: юзер
    :return: None
    """
    
    result, key, step = MyStyleCalendar(calendar_id=1, min_date=date.today(), locale='ru').process(callback.data)
    if not result and key:
        bot.edit_message_text(
            f"Выберите {bot_config.calendar.locale[step]}",
            callback.message.chat.id,
            callback.message.message_id,
            reply_markup=key
        )
    
    elif result:
        bot.edit_message_text(
            f"Дата прибытия <{result}>",
            callback.message.chat.id,
            callback.message.message_id
        )
        logger.info(result)
        logger.info(type(result))
        
        user_data.trip_check_in = int(date_to_unix(f'{result}'))
        user_data.save()
        
        text = "Выберите дату выбытия: "
        bot.send_message(callback.message.chat.id, text)
        calendar, step = MyStyleCalendar(calendar_id=2, min_date=result, locale='ru').build()
        bot.send_message(
            callback.message.chat.id,
            f"Дата выбытия {bot_config.calendar.locale[step]}",
            reply_markup=calendar
        )


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'bcc')
@cancel_decorator
@check_user_decorator
def callback_inline_currencies(call: CallbackQuery, user_data: User) -> None:
    """
    Стейт выбора точного местоположения с переходом на стейт выбора check in
    :param CallbackQuery call: колбэк
    :param User user_data: юзер
    :return: None
    """
    
    bot.edit_message_reply_markup(
        call.message.chat.id,
        call.message.message_id
    )
    commands_list = call.data.split(None, 2)
    logger.debug(commands_list)
    city_id = commands_list[1]
    city_name = commands_list[2]
    # value = ''
    bot.reply_to(call.message, f"Местоположение: {city_name}")
    if len(city_id) > 0:
        user_data.trip_dest_id = city_id
        user_data.trip_dest_name = city_name
        user_data.save()
        
        bot.set_state(call.message.chat.id, LowPriceState.date_check_in, call.message.chat.id)
        
        calendar, step = MyStyleCalendar(calendar_id=1, min_date=date.today(), locale='ru').build()
        bot.send_message(
            call.message.chat.id,
            f"Дата прибытия. Выберите {bot_config.calendar.locale[step]}",
            reply_markup=calendar)
    
    else:
        bot.set_state(call.message.chat.id, LowPriceState.city, call.message.chat.id)
        bot.reply_to(call.message, f"Указанное местоположение неверное. Введите город:")


@bot.message_handler(state=LowPriceState.city)
@cancel_decorator
@check_user_decorator
def get_city(message: Message, user_data: User) -> None:
    """
    Стейт ввода города с переходом на выбор точной локации
    :param Message message: сообщение
    :param User user_data: юзер
    :return: None
    """
    
    city = message.text
    message_find = bot.reply_to(
        message,
        f'Ищу совпадения по запросу "{city}"...'
    )
    
    reply_cancel = cancel_button()
    payload = {
        bot_config.requester.query_field: city,
        'locale': bot_config.requester.locale
    }
    
    logger.debug(f'{bot_config.requester.use_stub=}')
    
    if bot_config.requester.use_stub:
        json_path = os.path.join(bot_config.strings.project_dir, 'api', 'stub', f'request-{city}',
                                 'location-search.json')
        with open(json_path, encoding='utf8') as json_file:
            response = json.load(json_file)
    else:
        response = api_request(bot_config.requester.method_search_location, payload)
        if response is not False:
            response = json.loads(response)
    
    if response['rc'] == 'OK':
        result = response['sr']
        response = None
        if len(result) > 0:
            user_data.query = city
            user_data.save()
            bot.delete_message(message_find.chat.id, message_find.message_id)
            city_data: dict = result[0]
            city_rg: dict = city_data.get('regionNames', 'norg')
            city_name = city_rg.get('shortName', 'noname')
            cities_keyboard = current_city_buttons(result)
            bot.reply_to(
                message,
                f"Город найден: {city_name}. Уточните местоположение:",
                reply_markup=cities_keyboard
            )
            bot.set_state(
                message.chat.id,
                LowPriceState.current_city,
                message.chat.id
            )
        else:
            bot.reply_to(message, f'Город "{city}" в списке не найден. Повторите ввод!', reply_markup=reply_cancel)
    else:
        bot.reply_to(message, f'Ошибка при поиске "{city}". Повторите ввод!', reply_markup=reply_cancel)


@bot.message_handler(commands=['lowprice', 'highprice', 'bestdeal', ])
@check_user_decorator
def bot_low_price(message: Message, user_data: User) -> None:
    """
    Стартовые команды запроса поиска
    :param Message message: сообщение
    :param User user_data: юзер
    :return: None
    """
    
    command = message.text[1::]
    logger.info(f'Введённая команда: {command}')
    reply_cancel = cancel_button()
    logger.info(f'Запуск {command}')
    if user_data.is_complete > 0:
        reset_search(user_data, command)
        bot.set_state(message.chat.id, LowPriceState.city, message.chat.id)
        bot.send_message(message.chat.id, 'Введите город:', reply_markup=reply_cancel)
    else:
        bot.reply_to(
            message,
            f"Для того, чтобы начать пользоваться ботом, Вам необходимо настроить профиль. Это можно сделать здесь: /profile")
