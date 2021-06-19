from aiogram import executor
from bot import BOT_TOKEN, UTIL_URL
from events import *


if __name__ == '__main__':
    if BOT_TOKEN is None:
        bot_logger.critical("Токен для бота не определен!")
    if UTIL_URL is None:
        bot_logger.critical("URL Утилиты не определен!")
    else:
        executor.start_polling(dp)
    bot_logger.info("Бот завершил свою работу")
