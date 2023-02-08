import os.path

from loguru import logger
from config_data.currency import *
from peewee import *

db_path = "database.db"
db_path = os.path.join('database', db_path)
db = SqliteDatabase(db_path)


class BaseModel(Model):
    """
    Базовая модель (содержит primary key)
    """
    id = PrimaryKeyField(unique=True)
    
    class Meta:
        database = db
        order_by = 'id'


class User(BaseModel):
    """
    Модель Пользователя
    """
    username = CharField()  # username by telegram message
    user_id = IntegerField()  # идентификатор чата/пользователя
    hotel_numbers = IntegerField(default=10)  # hotel view numbers
    numbers_of_photo = IntegerField(default=0)  # amount of photos
    currency = CharField(5, default=USD)  # валюта
    price_min = IntegerField()  # минимальная цена
    price_max = IntegerField()  # максимальная цена
    distance = IntegerField()  # расстояние до центра
    is_complete = IntegerField(default=1)  # закончен ли опрос
    command = CharField(20)  # использованная команда
    query = CharField(20)  # использованная команда
    trip_check_in = IntegerField(default=0)  # дата въезда
    trip_check_out = IntegerField(default=0)  # дата выезда
    trip_dest_id = IntegerField(default=0)  # выбранный пункт назначения - ID
    trip_dest_name = CharField(100)  # выбранный пункт назначения - название
    
    class Meta:
        db_table = 'users'


class History(BaseModel):
    """
    Модель истории запросов пользователя
    """
    user_id = ForeignKeyField(User)  # User[id]
    command = CharField()
    command_time = DateField()
    currency = CharField()
    
    class Meta:
        db_table = 'history_commands'


class HotelsHistory(BaseModel):
    """
    Модель отеля, соотносящиеся с историей запросов
    """
    history_id = ForeignKeyField(History)
    hotel_id = IntegerField()
    name = CharField()
    address = CharField()
    by_center = FloatField()
    price = FloatField()
    
    class Meta:
        db_table = 'history_results'


class HotelsPhotos(BaseModel):
    """
    Модель фоток отелей по hotel_id
    """
    hotel_id = ForeignKeyField(HotelsHistory.hotel_id)
    url = TextField()
    
    class Meta:
        db_table = 'hotels_photos'


with db:
    tables = [User, History, HotelsHistory, HotelsPhotos]
    if not all(table.table_exists() for table in tables):
        db.create_tables(tables)
        logger.debug('Таблицы созданы успешно')
    else:
        logger.debug('Таблицы уже существуют')
