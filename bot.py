from uuid import UUID
from datetime import datetime
from aiocache import cached
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from config import BOT_TOKEN, UTIL_URL, STAND, ADMINS, bot_logger
from extension.utility import UtilityClient
from models.user import User


### Настройка бота.
bot = Bot(token=BOT_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)

# Утилита
util = UtilityClient(UTIL_URL, STAND)


def authentication(func):
    """Декоратор для проверки подлинности пользователя."""

    async def wrapper(*args):
        message, = args
        bot_logger.info(f"Получена команда '{message.text}' от пользователя '{message.from_user.full_name}'")

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
            '/cor [ProductGUID] - обновляет продукт через ядре \n'
            '/res [RequestGUID] - чинит кнопку. Изменяет состояние из 6 в 1.\n'
            '/pub [ProductGUID] - обновляет информацию о серте и лицензии\n'
            '/mail [ProductGUID] - узнать почту пользователя', reply_markup=keyboard)
    else:
        keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(KeyboardButton('/help'))
        keyboard.add(KeyboardButton('/register'))
        await message.answer(
            "Вы не авторизованы. "
            "Чтобы зарегистрироваться - подайте заявку с помощью команды /register",
            reply_markup=keyboard)


@dp.message_handler(commands=['register'])
@cached(ttl=60)
async def send_request_for_registration(message: types.Message):
    """Отправить заявку на регистрацию админам."""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/status'))

    if User.select().where(User.telegram_id == message.from_user.id).exists():
        await message.answer("Ваша заявка на регистрацию уже подана.\n", reply_markup=keyboard)
        return

    User.create(
        telegram_id=message.from_user.id,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
        full_name=message.from_user.full_name,
        mention=message.from_user.mention,
        username=message.from_user.username,
        url=message.from_user.url,
        is_bot=message.from_user.is_bot,
        is_active=False
    )
    bot_logger.info(f"Создана запись о пользователе '{message.from_user.full_name}'")

    inline_keyboard = InlineKeyboardMarkup()
    inline_keyboard.add(InlineKeyboardButton("Добавить", callback_data=f'add_user:{str(message.from_user.id)}'))

    for admin in ADMINS:
        await bot.send_message(
            chat_id=admin,
            text=f"Пользователь '{message.from_user.full_name}' {message.from_user.mention} запрашивает доступ к боту.",
            reply_markup=inline_keyboard)

    await message.answer(
        "Ваша заявка на регистрацию успешно создана.\n"
        "Периодически проверяйте доступ с помощью команды /status",
        reply_markup=keyboard)


@dp.callback_query_handler(lambda x: x.data.startswith('add_user'))
async def register_user(callback_query: types.CallbackQuery):
    """Регистрация пользователя."""
    await bot.answer_callback_query(callback_query.id)

    # извлекаем id пользователя из данных callback`a
    user_id = int(callback_query.data.split(':')[1])
    user = User.get_by_id(user_id)
    if user.is_active:
        await bot.send_message(callback_query.from_user.id, "Пользователь уже зарегистрирован")
        return

    user.is_active = True
    user.modification_date = datetime.now()
    user.save()
    bot_logger.info(f"Пользователь '{user.full_name}' успешно зарегистрирован")
    await bot.send_message(callback_query.from_user.id, "Пользователь зарегистрирован")


@dp.message_handler(commands=['status'])
@cached(ttl=60)
async def check_status(message: types.Message):
    """Проверить состояние регистрации пользователя."""
    user = User.get_or_none(telegram_id=message.from_user.id)
    if user:
        if user.is_active:
            await message.answer(
                "Вы зарегистрирвоаны! введите /help",
                reply_markup=ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton('/status')))
        else:
            await message.answer("Регисрация еще в процессе.")


@dp.message_handler(commands=['mail'])
@authentication
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
@authentication
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
@authentication
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
@authentication
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
@authentication
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
