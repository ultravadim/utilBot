import peewee
from datetime import datetime
from config import DATABASE


class User(peewee.Model):
    """Модель пользователя."""

    # Идентификатор пользователя в телеграме.
    telegram_id = peewee.IntegerField(primary_key=True)

    # Имя.
    first_name = peewee.CharField()

    # Фамилия.
    last_name = peewee.CharField()

    # Имя и Фамилия.
    full_name = peewee.CharField(max_length=512)

    # Обращение (@никнейм).
    mention = peewee.CharField()

    # Никнейм.
    username = peewee.CharField()

    # Ссылка на пользователя.
    url = peewee.CharField()

    # Признак бота.
    is_bot = peewee.BooleanField()

    # Признак активного пользователя.
    is_active = peewee.BooleanField(default=True)

    # Дата добавления.
    creation_date = peewee.DateTimeField(default=datetime.now)

    # Дата изменения.
    modification_date = peewee.DateTimeField()

    class Meta:
        database = DATABASE
        table_name = 'TelegramUser'

