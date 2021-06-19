"""
События по регистрации нового пользователя в боте
"""
from bot import dp
from models.user import User
from datetime import datetime
from aiocache import cached
from aiogram import types
from aiogram.types.reply_keyboard import KeyboardButton, ReplyKeyboardMarkup
from aiogram.types.inline_keyboard import InlineKeyboardButton, InlineKeyboardMarkup
from config import bot_logger, ADMINS



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
            await message.answer("Регистрация еще в процессе.")


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
