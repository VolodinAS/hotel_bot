from datetime import datetime
import time


def date_to_unix(date_string='') -> float:
    """
    Конвертация даты в unix
    :param date_string:
    :return: float
    """
    
    if len(date_string) > 0:
        return time.mktime(datetime.strptime(date_string, "%Y-%m-%d").timetuple())
    else:
        return time.time()


def unix_to_date(unix: str = '', date_format: str = '%d-%m-%Y') -> str | datetime:
    """
    Конвертация unix в дату по формату
    :param str unix: время (str для определения чисел)
    :param str date_format: формат времени
    :return: str | datetime
    """
    if str(unix).isdigit():
        return datetime.fromtimestamp(int(unix)).strftime(date_format)
    else:
        return datetime.fromtimestamp(date_to_unix())


def unix_to_dict(date_string: str) -> dict:
    """
    Переводим время unix в словарь (для запросов на апи по новой версии)
    :param str date_string: время
    :return: dict
    """
    date_data = date_string.split('-')
    return {
        'day': int(date_data[0]),
        'month': int(date_data[1]),
        'year': int(date_data[2])
    }
