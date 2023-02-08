import time

from database.models import History
from database.models import User


def add_new_history(user_data: User) -> History:
    """
    Добавляет новую историю поиска в БД
    :param User user_data: данные юзера
    :return: History
    """
    
    new_search: History = History(
        user_id=user_data.user_id,
        command=user_data.command,
        command_time=int(time.time()),
        currency=user_data.currency
    )
    new_search.save()
    return new_search
