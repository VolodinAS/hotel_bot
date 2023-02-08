from telebot.types import Message

from loader import bot
from loader import bot_config


@bot.message_handler(commands=['help',])
def bot_help(message: Message) -> None:
    """
    Отправить текст с командами
    :param Message message: сообщение
    :return: None
    """
    
    title = '\t\t➡<b>ПОМОЩЬ</b>⬅\n\n'
    text = [f'/{command} - {desk}\n' for command, desk in bot_config.tg_bot.commands]
    bot.reply_to(message, title + '\n'.join(text), parse_mode='HTML')
