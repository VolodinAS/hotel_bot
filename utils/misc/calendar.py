from telegram_bot_calendar import WYearTelegramCalendar


class MyStyleCalendar(WYearTelegramCalendar):
    """
    Кастомизация календаря
    """
    prev_button = "⬅️"
    next_button = "➡️"
    empty_month_button = ""
    empty_year_button = ""
