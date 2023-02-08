import json

from requests import Response

from api.api_request import api_request
from database.models import User
from loader import bot_config


def get_hotels_meta(hotel_id: str, user_data: User) -> Response | bool:
    """
    Получам данные по отелю - адрес и фотки
    :param str hotel_id: ид отеля
    :param User user_data: юзер
    :return: Response | bool
    """
    
    payload_photo = {
        'currency': user_data.currency,
        'eapid': bot_config.requester.default_payload_eapid,
        'locale': bot_config.requester.locale,
        'siteId': bot_config.requester.default_payload_siteId,
        'propertyId': hotel_id
    }
    
    response_photo = api_request(
        bot_config.requester.method_get_photo_info,
        payload_photo,
        bot_config.requester.method_get_photo_info_method
    )
    if response_photo is not False:
        return json.loads(response_photo)
    else:
        return response_photo
