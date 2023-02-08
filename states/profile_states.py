from telebot.handler_backends import State, StatesGroup


class UserInfoState(StatesGroup):
    """
    ГрупСтейты для анкеты профиля
    """
    currency = State()
    hotels = State()
    photos = State()
