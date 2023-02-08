from loguru import logger
from peewee import DoesNotExist
from telebot import types

from database.db_hotel import add_new_hotel
from database.db_photo import add_new_photo
from database.models import HotelsHistory
from database.models import HotelsPhotos
from database.models import User
from handlers.default_heandlers.error import bot_error
from loader import bot_config
from utils.misc.get_hotels_meta import get_hotels_meta
from utils.tag_wrapper import tag_wrapper


def parse_hotel_data(hotel_result: dict, user_data: User, new_history_id: int, total_days: int = 0) -> dict:
    """
    Получаем данные отеля из hotel_results
    :param dict hotel_result: данные отеля
    :param User user_data: юзер
    :param int new_history_id: ид истории
    :param int total_days: всего дней
    :return: dict
    """
    
    logger.debug('parse_hotel_data start')
    hotel_response = {
        'hotel_name': hotel_result['name'],  # "name": "Freedom Traveller"
        'hotel_id': str(hotel_result['id']),  # "id": "7783207"
        'hotel_price_float': float(hotel_result.get('price', {}).get('lead', {}).get('amount', 0)),
        'hotel_price_format': hotel_result.get('price', {}).get('lead', {}).get('formatted', 'не указано'),
        'hotel_price_total': 0,
        'hotel_media': []
    }
    
    logger.info(f'{total_days=}')
    
    if total_days > 0:
        hotel_response['hotel_price_total'] = round(total_days * hotel_response['hotel_price_float'])
    
    hotel_response['center'] = float(hotel_result.get('destinationInfo', {}).get('distanceFromDestination').get('value',
                                                                                                                bot_config.strings.max_dist))
    dest_measurement = hotel_result.get('destinationInfo', {}).get('distanceFromDestination').get('unit', 'nounit')
    
    if dest_measurement == 'MILE':
        if hotel_response['center'] != bot_config.strings.max_dist:
            hotel_response['center'] *= bot_config.strings.m_to_km
    
    responded_photo = None
    
    try:
        exists_hotel: HotelsHistory = HotelsHistory.get(HotelsHistory.hotel_id == int(hotel_response['hotel_id']))
        logger.info(f"Проверяем отель с id={hotel_response['hotel_id']}")
    except DoesNotExist:
        logger.info(f"Отеля id={hotel_response['hotel_id']} не существует. Создаём новую запись...")
        
        responded_photo = get_hotels_meta(hotel_response['hotel_id'], user_data)
        # pretty(responded_photo)
        if responded_photo is not False:
            response_data: dict = responded_photo.get('data', {})
            response_info: dict = response_data.get('propertyInfo', {})
            response_summary: dict = response_info.get('summary', {})
            response_location: dict = response_summary.get('location', {})
            response_address: dict = response_location.get('address', {})
            response_address_line = response_address.get('addressLine', 'не указано')
            
            hotel_response['hotel_address_format'] = response_address_line
            
            new_hotel: HotelsHistory = add_new_hotel(new_history_id, hotel_response, response_address_line)
        
        else:
            bot_error(user_data, '⚠ Ошибка при запросе к API')
            raise ConnectionError('Ошибка при запросе к API')
    else:
        hotel_response['hotel_address_format'] = exists_hotel.address
    
    exists_hotel: HotelsHistory = HotelsHistory.get(HotelsHistory.hotel_id == int(hotel_response['hotel_id']))
    
    summary_price = ''
    if total_days > 0:
        summary_price = f"\n" \
                        f"{tag_wrapper(f'Стоимость номера за {total_days} дней:')} {hotel_response['hotel_price_total']} {user_data.currency}"
    
    center_format = 'не указано'
    if hotel_response['center'] != bot_config.strings.max_dist:
        center_format = f"{hotel_response['center']} км"
    
    text = f"{tag_wrapper('Адрес:')} {hotel_response['hotel_address_format']}\n" \
           f"{tag_wrapper('Название:')} {hotel_response['hotel_name']}\n" \
           f"{tag_wrapper('Расстояние до центра:')} {center_format} км\n" \
           f"{tag_wrapper('Стоимость номера в сутки:')} {hotel_response['hotel_price_format']}" \
           f"{summary_price}"
    
    if user_data.numbers_of_photo > 0:
        logger.info('Требуются фото. Проверяем в БД')
        need_parse_photos = user_data.numbers_of_photo
        is_need_parse = False
        try:
            logger.info('запрос фоток')
            exists_hotel_photos: HotelsPhotos = HotelsPhotos. \
                select(). \
                group_by(HotelsPhotos.url). \
                where(HotelsPhotos.hotel_id == exists_hotel.hotel_id)
        except DoesNotExist:
            logger.info('фоток вообще нет')
            is_need_parse = True
        else:
            logger.info('фотки какие-то есть')
            if len(exists_hotel_photos) < need_parse_photos:
                need_parse_photos -= len(exists_hotel_photos)
                is_need_parse = True
            else:
                pass
        
        images_url = []
        if is_need_parse:
            logger.info('Парсим фото с добавлением в БД')
            if responded_photo is None:
                logger.info('responded_photo не загружался')
                responded_photo: dict = get_hotels_meta(hotel_response['hotel_id'], user_data)
            
            if responded_photo is not False:
                data: dict = responded_photo.get('data', {})
                propertyInfo: dict = data.get('propertyInfo', {})
                gallery: dict = propertyInfo.get('propertyGallery', {})
                images: list = gallery.get('images', [])
                if len(images) > 0:
                    photo_index = 0
                    while need_parse_photos > 0:
                        
                        try:
                            photo_data: dict = images[photo_index]
                        except IndexError:
                            need_parse_photos = 0
                        else:
                            photo_url = photo_data.get('image', {}).get('url')
                            
                            try:
                                exist_photo: HotelsPhotos = HotelsPhotos.get(HotelsPhotos.url == photo_url)
                            except DoesNotExist:
                                
                                new_photo: HotelsHistory = add_new_photo(exists_hotel, photo_url)
                                
                                photo_index += 1
                                need_parse_photos -= 1
                            else:
                                photo_url = exist_photo.url
                                photo_index += 1
                            
                            images_url.append(photo_url)
        
        else:
            for photo_db in exists_hotel_photos:
                images_url.append(photo_db.url)
        
        for photo_url in images_url:
            hotel_response['hotel_media'].append(types.InputMediaPhoto(photo_url))
    
    hotel_response['text'] = text
    logger.debug('parse_hotel_data end')
    return hotel_response
