from telebot.handler_backends import State, StatesGroup


class BestDealState(StatesGroup):
    """
    ГрупСтейты для bestdeal
    """
    price_min = State()
    price_max = State()
    distance = State()
