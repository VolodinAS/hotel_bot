from telebot.types import CallbackQuery
from telebot.types import Message

from config_data.currency import CURRENCIES
from database.models import History
from database.models import User
from keyboards.inline.currency import currency_inline_keyboard
from keyboards.inline.profile import profile_inline_keyboard
from loader import bot
from loader import bot_config
from states.profile_states import UserInfoState
from utils.check_user import check_user_decorator


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'currencies')
@check_user_decorator
def callback_inline_currencies(call: CallbackQuery, user_data: User) -> None:
    """
    Хендлер выбора валюты
    :param User user_data: данные пользователя
    :param CallbackQuery call: колбэк
    :return: None
    """
    
    commands_list = call.data.split()
    value = commands_list[1]
    if value in CURRENCIES:
        bot.reply_to(call.message, f"Валюта: {CURRENCIES[value]['title']}")
        bot.set_state(call.message.chat.id, UserInfoState.hotels, call.message.chat.id)
        bot.reply_to(call.message, 'Введите количество отображаемых отелей (1 - 20):')
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
        user_data.currency = value
        user_data.save()
    else:
        bot.reply_to(call.message, 'Данной валюты нет в списке доступных')


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'repeat')
@check_user_decorator
def callback_inline_repeat(call, user_data: User) -> None:
    """
    Хендлер повторного заполнения профиля
    :param User user_data: данные пользователя
    :param CallbackQuery call: сообщение пользователя
    :return: None
    """
    
    inline_currency = currency_inline_keyboard()
    bot.set_state(call.message.chat.id, UserInfoState.currency, call.message.chat.id)
    bot.reply_to(call.message, 'Выберите желаемую отображаемую валюту (из-за нового API доступно только USD):',
                 reply_markup=inline_currency)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    user_data.is_complete = 0
    user_data.save()


@bot.callback_query_handler(func=lambda call: call.data.split()[0] == 'clear_history')
@check_user_decorator
def callback_inline_clear_history(call: CallbackQuery, user_data: User) -> None:
    """
    Хендлер очистки истории поиска
    :param User user_data: данные пользователя
    :param CallbackQuery call: сообщение пользователя
    :return: None
    """
    
    print(type(call))
    
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)
    clear_history = History.delete().where(History.user_id == user_data.user_id)
    is_clear = clear_history.execute()
    text = 'Удалять нечего'
    if is_clear > 0:
        text = f'История успешно очищена! Удалено запросов: {is_clear}'
    bot.send_message(
        chat_id=call.message.chat.id,
        text=text
    )


@bot.message_handler(state=UserInfoState.hotels)
@check_user_decorator
def get_hotels(message: Message, user_data: User) -> None:
    """
    Хендлер количества отелей
    :param User user_data: данные пользователя
    :param Message message: сообщение пользователя
    :return: None
    """
    
    hotels = message.text
    if hotels.isdigit() and (1 <= int(hotels) <= 20):
        
        bot.reply_to(message, f'Отелей: {message.text}')
        user_data.hotel_numbers = int(hotels)
        user_data.save()
        
        bot.send_message(message.chat.id, 'Сколько фото отображать? (0 - 5):')
        bot.set_state(message.chat.id, UserInfoState.photos, message.chat.id)
        bot.edit_message_reply_markup(message.chat.id, message.message_id)
    
    else:
        bot.reply_to(message, f'Неправильное количество')


@bot.message_handler(state=UserInfoState.photos)
@check_user_decorator
def get_photos(message: Message, user_data: User) -> None:
    """
    Хендлер количества фото
    :param User user_data: данные пользователя
    :param Message message: сообщение пользователя
    :return: None
    """
    
    photos = message.text
    if photos.isdigit() and (0 <= int(photos) <= 5):
        bot.reply_to(message, f'Фотографий: {message.text}')
        user_data.numbers_of_photo = int(photos)
        user_data.is_complete = 1
        user_data.save()
        bot.delete_state(chat_id=message.chat.id, user_id=message.from_user.id)
        
        bot.send_message(message.chat.id, '💾 Настройки сохранены')
        text = [f'/{command} - {desk}\n' for command, desk in bot_config.tg_bot.func_commands]
        bot.send_message(message.chat.id, '\n'.join(text), parse_mode='HTML')
    else:
        bot.reply_to(message, f'Неправильное количество')


@bot.message_handler(commands=['profile',])
@check_user_decorator
def bot_profile(message: Message, user_data: User) -> None:
    """
    Хендлер профиля
    :param User user_data: данные пользователя
    :param Message message: сообщение пользователя
    :return: None
    """
    
    title = '\t\t➡<b>ПРОФИЛЬ</b>⬅\n\n'
    
    inline_profile = profile_inline_keyboard()
    MSG = title
    MSG += f'<b>Имя:</b> {user_data.username}\n'
    MSG += f"<b>Валюта:</b> {CURRENCIES[user_data.currency]['title']}\n"
    MSG += f"<b>Показывать отелей:</b> {user_data.hotel_numbers}\n"
    MSG += f"<b>Показывать фото:</b> {user_data.numbers_of_photo}\n"
    bot.reply_to(message, MSG, parse_mode='HTML', reply_markup=inline_profile)
