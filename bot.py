from uuid import UUID
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, UTIL_URL, STAND, bot_logger
from extension.utility import UtilityClient


### Настройка бота.
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Утилита
util = UtilityClient(UTIL_URL, STAND)


def log_command(func):
    """Декоратор для логирования команды."""
    async def wrapper(*args):
        message, = args
        bot_logger.info(f"Получена команда '{message.text}' от пользователя '{message.from_user.full_name}'")
        await func(*args)
    return wrapper


def validate_guid(guid: str) -> bool:
    """Проверить валидность Guid."""
    try:
        UUID(guid)
        return True
    except ValueError:
        bot_logger.error(f"GUID: '{guid}' имеет неверный формат!")
        return False


@dp.message_handler(commands=['start', 'help'])
async def welcome_message(message: types.Message):
    await message.answer(
        '<b>Доступные методы:</b>\n'
        '/req [RequestGUID] - обновляет статус заявки\n'
        '/cor [ProductGUID] - обновляет продукт через ядре \n'
        '/res [RequestGUID] - чинит кнопку. Изменяет состояние из 6 в 1.\n'
        '/pub [ProductGUID] - обновляет информацию о серте и лицензии\n'
        '/mail [ProductGUID] - узнать почту пользователя'
    )


@dp.message_handler(commands=['mail'])
@log_command
async def get_mail(message: types.Message):
    # Проверяем наличие GUID в сообщении
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Команда позволяет по GUID продукта узнать почту.')
        return

    # Валидируем guid
    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    # Выполняем запрос на обновление.
    response_message = await util.get_email(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['pub'])
@log_command
async def publish_product_info(message: types.Message):
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Публикация сообщения о лицензии, сертификате, доверенности.')
        return

    if not validate_guid:
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = await util.publish_info(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['res'])
@log_command
async def reset_request_status(message: types.Message):
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Сбросить заявку со статуса CertRequestCreation (6) в черновик (1).\n'
                             'Зависшая заявка, отсутствует кнопка отправить заявление.')
        return

    if not validate_guid(guid):
        await message.answer('GUID заявки указан некорректно.')
        return

    response_message = await util.reset_request_status(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['req'])
@log_command
async def update_request(message: types.Message):
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Обновление данных заявки')
        return

    if not validate_guid(guid):
        await message.answer('GUID заявки указан некорректно.')
        return

    response_message = await util.update_request_status(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['cor'])
@log_command
async def update_abonents(message: types.Message):
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Обновление данных организации с веб-регистратора через Ядро')
        return

    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = await util.update_abonents(guid)
    await message.answer(response_message)


if __name__ == '__main__':
    if BOT_TOKEN is None:
        bot_logger.critical("Токен для бота не определен!")
    if UTIL_URL is None:
        bot_logger.critical("URL Утилиты не определен!")
    else:
        executor.start_polling(dp)
    bot_logger.info("Бот завершил свою работу")
