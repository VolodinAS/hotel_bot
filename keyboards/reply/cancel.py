from collections.abc import Callable
from typing import Any

import telebot
from telebot import types
from telebot.types import CallbackQuery
from telebot.types import Message
from telebot.types import ReplyKeyboardMarkup

from config_data.config import *
from loader import bot
from loader import bot_config


def cancel_button() -> ReplyKeyboardMarkup:
    """
    Кнопка отмена ввода команды
    :return: InlineKeyboardMarkup
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    cancel = types.KeyboardButton(text=bot_config.strings.cancel_button)
    markup.add(cancel)
    return markup


def get_instance_message(input_instance: CallbackQuery) -> Message | CallbackQuery | None:
    """
    Определение того, какой инстанс пришел в коллбек - Message или CallbackQuery
    :param CallbackQuery input_instance:
    :return:
    """
    if isinstance(input_instance, telebot.types.CallbackQuery):
        return input_instance.message
    elif isinstance(input_instance, telebot.types.Message):
        return input_instance
    else:
        logger.error(f'Ожидался CallbackQuery или Message, пришло {type(input_instance)}')
        return None


def cancel_decorator(func: Callable) -> Callable:
    """
    Декоратор. Определяет, пришло ли в хендлер сообщение о том, что надо отменить дальнейший ввод команд
    :param Callable func: обворачиваемая функция (которая внутри хендлера)
    :return: Callable
    """
    def wrapper(input_instance: CallbackQuery) -> Any | Any:
        """
        Декоратор wrapper. Определяет, есть ли отмена
        :param CallbackQuery input_instance: пришедший инстанс
        :return:
        """
        if isinstance(input_instance, telebot.types.CallbackQuery):
            msg_instance = input_instance.message
            is_cancel = msg_instance.text
        elif isinstance(input_instance, telebot.types.Message):
            msg_instance = input_instance
            is_cancel = msg_instance.text
        else:
            logger.error(f'Ожидался CallbackQuery или Message, пришло {type(input_instance)}')
            is_cancel = None
        
        if is_cancel == bot_config.strings.cancel_button:
            logger.info('ВЫЗВАНО ПРЕРЫВАНИЕ КОМАНДЫ')
            # bot.delete_state(chat_id=msg_instance.chat.id, user_id=msg_instance.from_user.id)
            # bot.delete_message(msg_instance.chat.id, msg_instance.message_id)
            # a = types.ReplyKeyboardRemove()
            # bot.send_message(msg_instance.chat.id, 'Ввод команды отменён...', reply_markup=a)
            
            go_cancel(msg_instance)
        
        else:
            func(input_instance)
    
    return wrapper


def go_cancel(msg_instance: Message, need_delete: bool = True) -> None:
    """
    Закрыватель стейта (при отмене или возникновении ошибки)
    :param Message msg_instance: инстанс последнего сообщения
    :param bool need_delete: нужно ли удалять переданное сообщение
    :return:
    """
    bot.delete_state(
        user_id=msg_instance.chat.id,
        chat_id=msg_instance.chat.id
    )
    if need_delete:
        bot.delete_message(msg_instance.chat.id, msg_instance.message_id)
    empty_keyboard = types.ReplyKeyboardRemove()
    message_cancel: Message = bot.send_message(msg_instance.chat.id, 'Ввод команды отменён...',
                                               reply_markup=empty_keyboard)
    bot.delete_message(message_cancel.chat.id, message_cancel.message_id)
