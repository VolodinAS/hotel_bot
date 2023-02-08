from telebot.types import Message

from database.models import User
from keyboards.inline.confirm import confirm_trip_inline
from keyboards.reply.cancel import cancel_decorator
from loader import bot
from states.bestdeal_states import BestDealState
from utils.check_user import check_user_decorator
from utils.date_and_unix import unix_to_date


@bot.message_handler(state=BestDealState.distance)
@cancel_decorator
@check_user_decorator
def get_price_max(message: Message, user_data: User) -> None:
    """
    Стейт дистанции с переходом подтверждение поиска
    :param Message message: сообщение
    :param User user_data: юзер
    :return: None
    """
    
    distance = message.text
    
    if distance.isdigit():
        distance = int(distance)
        
        user_data.distance = distance
        user_data.save()
        
        confirm_me = confirm_trip_inline(user_data.command)
        text = f'' \
               f'Подтвердите поиск:' \
               f'\n\nВыбранный город: {user_data.trip_dest_name}' \
               f'\n\nДата прибытия: {unix_to_date(user_data.trip_check_in)}' \
               f'\n\nДата выбытия: {unix_to_date(user_data.trip_check_out)}' \
               f'\n\nКоличество отелей: {user_data.hotel_numbers}' \
               f'\n\nКоличество фото: {user_data.numbers_of_photo}' \
               f'\n\nМинимальная цена: {user_data.price_min} {user_data.currency}' \
               f'\n\nМаксимальная цена: {user_data.price_max} {user_data.currency}' \
               f'\n\nДопустимое расстояние до центра: {user_data.distance} км'
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=confirm_me
        )
    
    else:
        bot.reply_to(message=message, text='Вы ввели не число. Повторите ввод минимальной цены:')


@bot.message_handler(state=BestDealState.price_max)
@cancel_decorator
@check_user_decorator
def get_price_max(message: Message, user_data: User) -> None:
    """
    Стейт максимальной цены с переходом на дистанцию
    :param Message message: сообщение
    :param User user_data: юзер
    :return: None
    """
    
    price_max = message.text
    
    if price_max.isdigit():
        price_max = int(price_max)
        if price_max > user_data.price_min:
            
            user_data.price_max = price_max
            user_data.save()
            
            bot.send_message(message.chat.id, f'Укажите допустимое расстояние до центра (в км):')
            bot.set_state(
                user_id=message.chat.id,
                chat_id=message.chat.id,
                state=BestDealState.distance,
            )
        else:
            bot.reply_to(message=message,
                         text='Максимальная цена должна быть больше минимальной. Повторите ввод максимальной цены:')
    else:
        bot.reply_to(message=message, text='Вы ввели не число. Повторите ввод максимальной цены:')


@bot.message_handler(state=BestDealState.price_min)
@cancel_decorator
@check_user_decorator
def get_price_min(message: Message, user_data: User) -> None:
    """
    Стейт минимальной цены с переходом на максимальную цену
    :param Message message: сообщение
    :param User user_data: юзер
    :return: None
    """
    
    price_min = message.text
    
    if price_min.isdigit():
        price_min = int(price_min)
        if price_min == 0:
            price_min = 1
        
        user_data.price_min = price_min
        user_data.save()
        bot.send_message(message.chat.id, f'Укажите максимальную искомую цену (в {user_data.currency}):')
        bot.set_state(
            user_id=message.chat.id,
            chat_id=message.chat.id,
            state=BestDealState.price_max,
        )
    else:
        bot.reply_to(message=message, text='Вы ввели не число. Повторите ввод минимальной цены:')
