import re
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, UTIL_URL, bot_logger
from util.methods import Method


### Константы.
regular_guid = '[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}|[a-zA-Z0-9]{32}'

### Настройка бота.
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Утилита
util = Method(UTIL_URL)


def validate_guid(guid: str) -> bool:
    """Проверить валидность Guid."""
    if re.match(regular_guid, guid):
        return True
    bot_logger.error(f"GUID: {guid} имеет неверный формат!")
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
async def get_mail(message: types.Message):
    # Проверяем наличие GUID в сообщении
    if len(message.text.split(' ')) != 2:
        await message.answer('Команда позволяет по GUID продукта узнать почту.')
        return

    # Забираем GUID из сообщения и проверяем по регулярке
    guid = message.text.split(maxsplit=1)[1]
    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    # Выполняем запрос на обновление и смотрим ответ, если True отдаем пользователю информацию.
    response_message = util.mail(guid, 'prod')
    if response_message['success']:
        await message.answer(response_message['message']['email'])
    else:
        await message.answer(response_message['message'])


@dp.message_handler(commands=['pub'])
async def publish_product_info(message: types.Message):
    if len(message.text.split(' ')) != 2:
        await message.answer('Публикация сообщения о лицензии, сертификате, доверенности.')
        return

    guid = message.text.split(maxsplit=1)[1]
    if not validate_guid:
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = util.publish_info(guid, 'prod')
    if response_message['success']:
        await message.answer(response_message['message'])
    else:
        await message.answer(response_message['message']['errorMessage'])


@dp.message_handler(commands=['res'])
async def reset_request_status(message: types.Message):
    if len(message.text.split(' ')) != 2:
        await message.answer('Сбросить заявку со статуса CertRequestCreation (6) в черновик (1).\n'
                             'Зависшая заявка, отсутствует кнопка отправить заявление.')
        return

    guid = message.text.split(maxsplit=1)[1]
    if not validate_guid(guid):
        await message.answer('GUID заявки указан некорректно.')
        return

    response_message = util.reset_request_status(guid, 'prod')
    await message.answer(response_message['message'])


@dp.message_handler(commands=['req'])
async def update_request(message: types.Message):
    if len(message.text.split(' ')) != 2:
        await message.answer('Обновление данных заявки')
        return

    guid = message.text.split(maxsplit=1)[1]
    if not validate_guid(guid):
        await message.answer('GUID заявки указан некорректно.')
        return

    response_message = util.update_request_status(guid, 'prod')
    if response_message['success']:
        await message.answer(response_message['message'])
    else:
        await message.answer(response_message['message']['errorMessage'])


@dp.message_handler(commands=['cor'])
async def updateAbonents(message: types.Message):
    if len(message.text.split(' ')) != 2:
        await message.answer('Обновление данных организации с веб-регистратора через Ядро')
        return

    guid = message.text.split(maxsplit=1)[1]
    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    # Отправляем запрос, ответ приходит в формате JSON.
    # Для определения, что было сделано, пройдем по JSON циклом
    response_message = util.update_abonents(guid, 'prod')
    server_message = ''
    for key, value in response_message['message'].items():
        if value:
            server_message += f'{key.capitalize()}: {value[0]}'

    # Если обновления были, отдаем пользователю.
    if server_message:
        await message.answer(server_message)
    else:
        await message.answer('Обновления не произошли.')


if __name__ == '__main__':
    if BOT_TOKEN is None:
        bot_logger.critical("Токен для бота не определен!")
    if UTIL_URL is None:
        bot_logger.critical("URL Утилиты не определен!")
    else:
        executor.start_polling(dp)
    bot_logger.info("Бот завершил свою работу")
