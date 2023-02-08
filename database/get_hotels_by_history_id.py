from database.models import HotelsHistory


def get_hotels_by_history_id(history_id) -> HotelsHistory:
    """
    Получаем данные отеля из БД по ид
    :param int history_id: ид отеля
    :return: HotelsHistory
    """
    
    history: HotelsHistory = HotelsHistory. \
        select(). \
        where(HotelsHistory.history_id == history_id)
    
    return history
