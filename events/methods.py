"""
События по использовнию методов утилы.
"""
from bot import util, dp
from uuid import UUID
from models.user import User
from aiocache import cached
from config import bot_logger
from aiogram import types
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup


def authentication(func):
    """Декоратор для проверки подлинности пользователя."""

    async def wrapper(*args):
        message, = args
        bot_logger.info(f"Получена команда '{message.text}' от пользователя "
                        f"'{message.from_user.full_name} | {message.from_user.mention}'")

        if not User.select().where(User.telegram_id == message.from_user.id, User.is_active).exists():
            bot_logger.warning(f"Пользователь id={message.from_user.id} '{message.from_user.full_name}' не зарегистрирован")
            await message.answer('Нет прав. Обратитесь к разработчику')
            return

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
@cached(ttl=60)
async def welcome_message(message: types.Message):
    if User.select().where(User.telegram_id == message.from_user.id, User.is_active).exists():
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/help'))
        await message.answer(
            '<b>Доступные методы:</b>\n'
            '/req [RequestGUID] - обновляет статус заявки\n'
            '/cor [ProductGUID] - обновляет продукт через ядро \n'
            '/res [RequestGUID] - чинит кнопку. Изменяет состояние из 6 в 1.\n'
            '/pub [ProductGUID] - обновляет информацию о серте и лицензии\n'
            '/mail [ProductGUID] - узнать почту пользователя\n'
            '/add [ProductGUID] - добавить организацию в white list', reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('/help'))
        keyboard.add(KeyboardButton('/register'))
        await message.answer(
            "Вы не авторизованы. "
            "Чтобы зарегистрироваться - подайте заявку с помощью команды /register",
            reply_markup=keyboard)


@dp.message_handler(commands=['mail'])
@authentication
async def get_mail(message: types.Message):
    """Получить email по product_guid."""

    guid = message.get_args().strip()
    if not guid:
        await message.answer('Команда позволяет по GUID продукта узнать почту.')
        return

    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = await util.get_email(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['pub'])
@authentication
async def publish_product_info(message: types.Message):
    """Опубликовать сообщение о лицензии, серте, доверке."""
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
@authentication
async def reset_request_status(message: types.Message):
    """Сбросить статус заявки, застрявшей в 6 статусе."""
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
@authentication
async def update_request(message: types.Message):
    """Обновить заявку."""
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
@authentication
async def update_abonents(message: types.Message):
    """Обновить абонента."""
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Обновление данных организации с веб-регистратора через Ядро')
        return

    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = await util.update_abonents(guid)
    await message.answer(response_message)


@dp.message_handler(commands=['add'])
@authentication
async def add_product_to_white_list(message: types.Message):
    """Добавить организацию в white list для миграции."""
    guid = message.get_args().strip()
    if not guid:
        await message.answer('Добавление организации в white list для миграции в АО5')
        return

    if not validate_guid(guid):
        await message.answer('GUID продукта указан некорректно.')
        return

    response_message = await util.add_to_white_list(guid)
    await message.answer(response_message)


