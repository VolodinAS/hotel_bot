from dataclasses import dataclass
import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger


@dataclass
class TeleBotData:
    """
    Тут храним данные бота
    """
    token: str
    admin_id: str
    commands: tuple
    func_commands: tuple


@dataclass
class StringsData:
    """
    Разные строки и числа
    """
    cancel_button: str
    project_dir: str
    history_amount: int
    commands_desc: dict
    m_to_km: float
    max_dist: int


@dataclass
class RapidApiData:
    """
    Данные для rapidapi
    """
    api_key: str
    url: str
    hotel_url: str


@dataclass
class CurrateData:
    """
    Данные по парсингу валют (не работает)
    """
    api_key: str
    url: str


@dataclass
class CalendarData:
    """Настройка языка календаря"""
    locale: dict


@dataclass
class RequestData:
    """
    Различные данные для запросов на апи
    """
    use_stub: bool
    sort: str
    sort_best: str
    query_field: str
    locale: str
    method_search_location: str
    method_search_location_method: str
    method_get_hotels: str
    method_get_hotels_method: str
    method_get_photo_info: str
    method_get_photo_info_method: str
    default_payload_eapid: int
    default_payload_siteId: int
    default_payload_resultsStartingIndex: int
    default_payload_rooms: list
    default_payload_filters: dict
    headers: dict


@dataclass
class Config:
    """
    Объединение данных в один конфиг
    """
    tg_bot: TeleBotData
    rapid_api: RapidApiData
    strings: StringsData
    currency: CurrateData
    requester: RequestData
    calendar: CalendarData


def load_config() -> Config:
    """
    Создаем конфиг
    :return: Config
    """
    if not find_dotenv():
        exit('Переменные окружения не загружены т.к отсутствует файл .env')
    else:
        load_dotenv()
    
    use_stub = int(os.getenv('USE_STUB'))
    
    logger.debug(f'{use_stub=}')
    
    config = Config(
        
        tg_bot=TeleBotData(
            token=os.getenv('BOT_TOKEN'),
            admin_id=os.getenv('ADMIN_ID'),
            commands=(
                ('start', "Запустить бота"),
                ('help', "Вывести справку"),
                ('profile', "Профиль, настройки поиска"),
                ('lowprice', "Топ самых дешёвых отелей в городе"),
                ('highprice', "Топ самых дорогих отелей в городе"),
                ('bestdeal',
                 "Топ отелей, наиболее подходящих по цене и расположению от центра (самые дешёвые и находятся ближе всего к центру)"),
                ('history', "История запросов"),
            ),
            func_commands=(
                ('lowprice', "Топ самых дешёвых отелей в городе"),
                ('highprice', "Топ самых дорогих отелей в городе"),
                ('bestdeal',
                 "Топ отелей, наиболее подходящих по цене и расположению от центра (самые дешёвые и находятся ближе всего к центру)"),
            )
        ),
        
        rapid_api=RapidApiData(
            api_key=os.getenv('RAPID_API_KEY'),
            url=os.getenv('RAPID_API_URL'),
            hotel_url=os.getenv('RAPID_HOTEL_URL')
        ),
        
        currency=CurrateData(
            api_key=os.getenv('CURRENCY_API_KEY'),
            url=os.getenv('CURRENCY_URL')
            # https://currate.ru/
            # {"status":"200","message":"rates","data":{"EURRUB":"71.3846","USDRUB":"58.059"}}
        ),
        
        strings=StringsData(
            cancel_button='Отменить команду',
            project_dir=os.getcwd(),
            history_amount=int(os.getenv('HISTORY_LIMIT')),
            commands_desc={
                'lowprice': 'Мин. цены',
                'highprice': 'Макс. цены',
                'bestdeal': 'Опт. цены'
            },
            m_to_km=1.60934,
            max_dist=99999
        ),
        
        calendar=CalendarData(
            locale={
                'y': 'год',
                'm': 'месяц',
                'd': 'день'
            }
        ),
        
        requester=RequestData(
            use_stub=bool(use_stub),
            sort='PRICE_LOW_TO_HIGH',
            sort_best='DISTANCE',
            query_field='q',
            locale='ru_RU',
            method_search_location='locations/v3/search',
            method_search_location_method='GET',
            method_get_photo_info='properties/v2/detail',
            method_get_photo_info_method='POST',
            method_get_hotels='properties/v2/list',
            method_get_hotels_method='POST',
            default_payload_eapid=1,
            default_payload_siteId=300000001,
            default_payload_resultsStartingIndex=0,
            default_payload_rooms=[
                {
                    "adults": 1
                }
            ],
            default_payload_filters={
                "availableFilter": "SHOW_AVAILABLE_ONLY"
            },
            headers={}
        )
    )
    
    config.requester.headers = {
        "X-RapidAPI-Key": config.rapid_api.api_key,
        "X-RapidAPI-Host": config.rapid_api.url
    }
    
    logger.debug(f'{config.requester.use_stub=}')
    
    return config
