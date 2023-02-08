from telebot.types import Message

from database.models import User
from keyboards.reply.cancel import go_cancel
from loader import bot


def bot_error(user_data: User, msg: str) -> None:
    """
    Функция отправки сообщения юзеру, что на стороне сервера возникла ошибка, сброс состояний
    :param str msg: сообщение для пользователя
    :param User user_data: юзер
    :return: None
    """
    message_error: Message = bot.send_message(
        chat_id=user_data.user_id,
        text=msg
    )
    go_cancel(message_error, False)
