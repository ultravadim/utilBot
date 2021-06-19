from aiogram import Bot, Dispatcher, types
from extension.utility import UtilityClient
from config import BOT_TOKEN, UTIL_URL, STAND


bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

util = UtilityClient(UTIL_URL, STAND)
