from loguru import logger
from telebot import types
from telebot.types import InlineKeyboardMarkup
from telebot.types import Message

from database.models import History, HotelsHistory
from loader import bot_config
from utils.date_and_unix import unix_to_date
from utils.pretty import pretty


def history_buttons_inline(history_buttons: list, message_find: Message) -> InlineKeyboardMarkup:
    """
    Кнопки последних нескольких историй
    :param: list history_buttons список истории поиска
    :param: Message message_find сообщение
    :return: InlineKeyboardMarkup
    """
    history = types.InlineKeyboardMarkup(row_width=1)
    history_button: History
    for history_button in history_buttons:
        
        hotels_amount: HotelsHistory = HotelsHistory.select(HotelsHistory.id).where(HotelsHistory.history_id == history_button.id)
        
        callback_history = f'show_history {history_button.id} {message_find.message_id}'
        logger.info(callback_history)
        key_history = types.InlineKeyboardButton(
            f"[#{history_button.id}] "
            f"{bot_config.strings.commands_desc[history_button.command]} "
            f"от {unix_to_date(history_button.command_time, '%d-%m-%Y  %H:%M:%S')}, "
            f"отелей: {len(hotels_amount)}",
            callback_data=callback_history
        )
        history.add(key_history)
        
    return history
