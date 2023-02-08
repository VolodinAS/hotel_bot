from telebot import types
from telebot.types import Message

from loader import bot
from loader import bot_config


# Эхо хендлер, куда летят текстовые сообщения без указанного состояния
@bot.message_handler(state=None)
def bot_echo(message: Message) -> None:
    """
    Эхо-стейт с поддержкой нажатия кнопки Отмена
    :param Message message: сообщение
    :return: None
    """
    if message.text == bot_config.strings.cancel_button:
        empty_keyboard = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Отмена...', reply_markup=empty_keyboard)
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_state(chat_id=message.chat.id, user_id=message.from_user.id)
    else:
        bot.reply_to(message, "Неопознанная команда. Для просмотра команд введите /help")
