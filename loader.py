import urllib3
from telebot import TeleBot
from telebot.storage import StateMemoryStorage

from config_data.config import Config
from config_data.config import load_config

storage = StateMemoryStorage()
bot_config: Config = load_config()
bot = TeleBot(token=bot_config.tg_bot.token, state_storage=storage)
http = urllib3.PoolManager()
