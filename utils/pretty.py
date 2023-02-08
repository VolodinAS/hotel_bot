import json


def pretty(obj: json) -> None:
    """
    Красивое форматирование вывода dict
    :param obj: объект
    :return: None
    """
    json_formatted_str = json.dumps(obj, indent=4, ensure_ascii=False)
    print(json_formatted_str)
