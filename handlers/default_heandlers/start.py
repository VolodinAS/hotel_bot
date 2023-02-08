from telebot.types import Message

from database.models import *
from loader import bot
from utils.check_user import autocheck_user


@bot.message_handler(commands=['start', ])
def bot_start(message: Message) -> None:
    """
    Хендлер старта
    :param Message message: сообщение пользователя
    :return: None
    """
    
    user_name = message.from_user.username
    
    GREETINGS = f'Добро пожаловать, @{user_name}!'
    MSG = "Введите нужную Вам команду для начала работы."
    
    user_data = autocheck_user(message.from_user)
    if user_data['result']:
        if not user_data['is_new']:
            GREETINGS = f'Рады Вас видеть, @{user_name}!'
        
        user: User = user_data['user']
        if user.is_complete == 0:
            bot.reply_to(message, GREETINGS + ' Необходимо заполнить данные профиля!')
        else:
            bot.reply_to(message, GREETINGS + ' ' + MSG)
    else:
        bot.reply_to(message, MSG)
