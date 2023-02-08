import requests
from loguru import logger
from requests import Response

from loader import bot_config


def api_request(method: str, params: dict, method_type: str = 'GET') -> str | bool:
    """
    Общая функция запроса на апи
    :param str method: к какому методу апи сделать запрос
    :param dict params: параметры запроса
    :param str method_type: метод отправляемых данных
    :return: str | bool
    """
    params['locale'] = bot_config.requester.locale
    
    url = f"https://{bot_config.rapid_api.url}/{method}"
    
    if method_type == 'GET' or method_type == 'POST':
        logger.info('ДАННЫЕ ЗАПРОСА')
        logger.debug(f'{method_type}-запрос на URL: {url}')
        
        if method_type == 'GET':
            return get_request(
                url=url,
                params=params
            )
        else:
            return post_request(
                url=url,
                params=params
            )
    else:
        logger.error(f'Ожидалось GET | POST, получен {method_type}')
        return False


def get_request(url: str, params: dict) -> str | bool:
    """
    Get-запрос
    :param str url: адрес
    :param dict params: параметры
    :return: str | bool
    """
    try:
        response: Response = requests.request(
            "GET",
            url,
            headers=bot_config.requester.headers,
            params=params,
            timeout=30
        )
    except requests.exceptions.RequestException as exc:
        logger.error(exc, exc_info=exc)
        return False

    if response.status_code == requests.codes.ok:
        logger.success('Ответ успешно получен')
        return response.text
    else:
        logger.error(f'Ошибка: {response.text}')
        return False


def post_request(url, params) -> str | bool:
    """
    Post-запрос
    :param str url: адрес
    :param dict params: параметры
    :return: str | bool
    """
    try:
        response: Response = requests.request(
            "POST",
            url,
            headers=bot_config.requester.headers,
            json=params,
            timeout=30
        )
    except requests.exceptions.RequestException as exc:
        logger.error(exc, exc_info=exc)
        return False
    
    if response.status_code == requests.codes.ok:
        logger.success('Ответ успешно получен')
        return response.text
    else:
        logger.error(f'Ошибка: {response.text}')
        return False
