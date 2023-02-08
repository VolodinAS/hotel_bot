from database.models import HotelsHistory
from database.models import HotelsPhotos


def add_new_photo(exists_hotel: HotelsHistory, photo_url: str) -> HotelsPhotos:
    """
    Добавление фото отеля в БД
    :param exists_hotel: модель отеля
    :param str photo_url:
    :return: HotelsPhotos
    """
    
    new_photo: HotelsPhotos = HotelsPhotos(
        hotel_id=exists_hotel.hotel_id,
        url=photo_url
    )
    new_photo.save()
    
    return new_photo
