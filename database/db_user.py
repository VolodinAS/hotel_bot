from database.models import User


def reset_search(user_data: User, command: str) -> None:
    """
    Сброс сохранённого статуса поиска пользователя
    :param User user_data: юзер
    :param str command: введённая команда
    :return: None
    """
    user_data.trip_check_in = 0
    user_data.trip_check_out = 0
    user_data.trip_dest_id = 0
    user_data.trip_dest_name = ''
    user_data.price_min = 0
    user_data.price_max = 0
    user_data.distance = 0
    user_data.query = ''
    user_data.command = command
    user_data.save()


def add_new_user(user_name: str, user_id: int) -> User:
    """
    Добавление юзера в БД
    :param str user_name: логин пользователя @
    :param int user_id: ид юзера
    :return:
    """
    new_user: User = User(
        username=user_name,
        user_id=user_id,
        trip_check_in=0,
        trip_check_out=0,
        price_min=0,
        price_max=0,
        distance=0,
        query='',
        trip_dest_name='',
        command='')
    
    new_user.save()
    
    return new_user
