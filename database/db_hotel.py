from database.models import History
from database.models import HotelsHistory


def add_new_hotel(new_history_id: int, hotel_response: dict, response_address_line: str) -> History:
    """
    Добавляет новый отел в БД
    :param str response_address_line: адрес отеля
    :param int new_history_id: ид истории
    :param dict hotel_response:
    :return: History
    """
    
    new_hotel: HotelsHistory = HotelsHistory(
        history_id=new_history_id,
        hotel_id=int(hotel_response['hotel_id']),
        name=hotel_response['hotel_name'],
        address=response_address_line,
        by_center=hotel_response['center'],
        price=hotel_response['hotel_price_float']
    )
    new_hotel.save()
    
    return new_hotel
