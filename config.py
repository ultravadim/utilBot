"""
Конфигурация проекта.
"""
import os
import dotenv
import logging
from playhouse.db_url import connect


# Загрузка переменных окружения из файла .env
dotenv.load_dotenv()

# токен телеграм бота.
BOT_TOKEN = os.environ.get('BOT_TOKEN', None)

# URL утилиты.
UTIL_URL = os.environ.get('UTIL_URL', None)

# Стенд, с которым будет работать утила
STAND = os.environ.get('STAND', 'prod')

# Список администраторов бота (id чатов в телеграме)
ADMINS = os.environ.get('ADMINS', '').split(';')

# Подключение к БД
DATABASE = connect(os.environ.get('DATABASE'))

### Настройка логгера.
bot_logger = logging.getLogger("bot")
bot_logger.setLevel(logging.INFO)

util_logger = logging.getLogger("utility")
util_logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('| %(asctime)s | %(name)-7s | - [%(levelname)s]: %(message)s'))

bot_logger.addHandler(handler)
util_logger.addHandler(handler)
