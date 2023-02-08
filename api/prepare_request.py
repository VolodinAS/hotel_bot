import json
import os

from telebot.types import Message

from api.api_request import api_request
from database.models import User
from handlers.default_heandlers.error import bot_error
from keyboards.reply.cancel import go_cancel
from loader import bot_config


def prepare_request(payload: dict, user_data: User, message_start: Message) -> str | bool:
    """
    Подготовка запроса в зависимости от настроек приложения - на API или stub-сервер
    :param dict payload: данные запроса
    :param User user_data: юзер
    :param Message message_start: сообщение
    :return:
    """
    if bot_config.requester.use_stub:
        json_path = os.path.join(bot_config.strings.project_dir, 'api', 'stub', f'request-{user_data.query}',
                                 'properties-list.json')
        with open(json_path, encoding='utf8') as json_file:
            response = json.load(json_file)
    else:
        response = api_request(
            bot_config.requester.method_get_hotels,
            payload,
            bot_config.requester.method_get_hotels_method
        )
        if response is not False:
            response = json.loads(response)
    
    if response is False:
        msg = 'Ошибка при запросе данных!'
        bot_error(user_data, msg)
        go_cancel(message_start, False)
        raise ConnectionError(msg)
    
    return response
