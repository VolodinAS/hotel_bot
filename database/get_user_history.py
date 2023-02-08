from database.models import History
from database.models import User
from loader import bot_config


def get_user_history(user_data: User) -> History:
    """
    Получение истории запросов пользователя
    :param User user_data: данные юзера
    :return: History
    """
    
    history: History = History. \
        select(). \
        where(History.user_id == user_data.user_id). \
        order_by(History.command_time.desc()). \
        limit(bot_config.strings.history_amount)
    
    return history
