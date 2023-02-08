from telebot import TeleBot
from telebot.types import BotCommand

from loader import bot_config


def set_default_commands(bot: TeleBot) -> None:
    """
    Установка команд для бота
    :param TeleBot bot: инстанс бота
    :return: None
    """
    
    bot.set_my_commands(
        [BotCommand(*i) for i in bot_config.tg_bot.commands]
    )
