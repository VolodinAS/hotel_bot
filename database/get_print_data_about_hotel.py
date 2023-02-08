from telebot import types

from database.models import HotelsHistory
from database.models import HotelsPhotos
from database.models import User
from utils.tag_wrapper import tag_wrapper


def get_print_data_about_hotel(hotel: HotelsHistory, user_data: User) -> dict:
    """
    Вывод данных по отелю в читабельный формат
    :param HotelsHistory hotel: данные отеля
    :param User user_data: данные пользователя
    :return: dict
    """
    
    hotel_info: dict = dict()
    photos: HotelsPhotos = HotelsPhotos.select().where(HotelsPhotos.hotel_id == hotel.hotel_id)
    media_url = []
    if len(photos) > 0:
        photo: HotelsPhotos
        for photo in photos:
            media_url.append(types.InputMediaPhoto(photo.url))
    
    if len(media_url) > 0:
        hotel_info['media'] = media_url
    else:
        hotel_info['media'] = False
    
    hotel_info['text'] = f"{tag_wrapper('Адрес:')} {hotel.address}\n" \
                         f"{tag_wrapper('Название:')} {hotel.name}\n" \
                         f"{tag_wrapper('Расстояние до центра:')} {hotel.by_center} км\n" \
                         f"{tag_wrapper('Стоимость номера в сутки:')} {hotel.price} {user_data.currency}"
    
    return hotel_info
