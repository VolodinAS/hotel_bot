from telebot.handler_backends import State, StatesGroup


class LowPriceState(StatesGroup):
    """
    ГрупСтейты для lowprice и highprice
    """
    city = State()
    current_city = State()
    date_check_in = State()
    date_check_out = State()
