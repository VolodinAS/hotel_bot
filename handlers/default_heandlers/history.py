from time import sleep

from telebot.types import CallbackQuery
from telebot.types import Message

from database.get_hotels_by_history_id import get_hotels_by_history_id
from database.get_print_data_about_hotel import get_print_data_about_hotel
from database.get_user_history import get_user_history
from database.models import HotelsHistory
from database.models import User
from keyboards.inline.history_buttons import history_buttons_inline
from keyboards.reply.cancel import go_cancel
from loader import bot
from loader import bot_config
from utils.check_user import check_user_decorator


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'show_history')
@check_user_decorator
def get_history_item(callback: CallbackQuery, user_data: User) -> None:
    """
    Хендлер истории поиска
    :param CallbackQuery callback: квери
    :param User user_data: юзер
    :return:
    """
    
    cc, history_id, message_id = callback.data.split()
    hotels = get_hotels_by_history_id(history_id)
    
    bot.edit_message_reply_markup(
        chat_id=user_data.user_id,
        message_id=message_id
    )
    
    if len(hotels) > 0:
        hotel: HotelsHistory
        for hotel in hotels:
            print_data = get_print_data_about_hotel(hotel, user_data)
            
            if print_data['media'] is not False:
                bot.send_media_group(
                    chat_id=user_data.user_id,
                    media=print_data['media']
                )
            bot.send_message(
                chat_id=user_data.user_id,
                text=print_data['text'],
                parse_mode='HTML'
            )
            sleep(1)
        message_end = bot.send_message(
            text='✅ Вывод результатов окончен!',
            chat_id=user_data.user_id
        )
        go_cancel(message_end, False)
    else:
        text = 'В данной истории запроса ПУСТО!'
        bot.edit_message_text(
            chat_id=user_data.user_id,
            message_id=message_id,
            text=text
        )


@bot.message_handler(commands=['history',])
@check_user_decorator
def get_history(message: Message, user_data: User) -> None:
    """
    Хендлер истории поиска
    :param Message message: сообщение
    :param User user_data: юзер
    :return:
    """
    
    message_find: Message = bot.send_message(
        chat_id=message.chat.id,
        text=f'История последних {bot_config.strings.history_amount}ти поисков...'
    )
    
    history_data = get_user_history(user_data)
    
    if len(history_data) > 0:
        
        history_buttons = history_buttons_inline(history_data, message_find)
        
        bot.edit_message_text(
            text=f'Ваша история запросов ({len(history_data)}):',
            chat_id=message_find.chat.id,
            message_id=message_find.id
        )
        
        bot.edit_message_reply_markup(
            chat_id=message_find.chat.id,
            message_id=message_find.id,
            reply_markup=history_buttons
        )
    
    else:
        bot.edit_message_text(
            text='У вас еще нет истории поиска!',
            chat_id=message_find.chat.id,
            message_id=message_find.id
        )
