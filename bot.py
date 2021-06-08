import re
import config
from util.methods import Method

from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
regular_guid = '[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}'
util = Method('http://util.ao5.in')


@dp.message_handler(commands=['start', 'help'])
async def welcome_message(message: types.Message):
    await message.answer('Welcome Message')


@dp.message_handler(commands=['mail'])
async def get_mail(message: types.Message):
    if len(message.text.split(' ')) == 2:
        guid = message.text.split(maxsplit=1)[1]
        if re.match(regular_guid, guid) is not None:
            response_message = util.mail(guid, 'prod')
            if response_message['success']:
                await message.answer(response_message['message']['email'])
            else:
                await message.answer(response_message['message'])
        else:
            await message.answer('GUID продукта указан некорректно.')
    else:
        await message.answer('Команда позволяет по GUID продукта узнать почту.')


@dp.message_handler(commands=['pub'])
async def publish_product_info(message: types.Message):
    if len(message.text.split(' ')) == 2:
        guid = message.text.split(maxsplit=1)[1]
        if re.match(regular_guid, guid) is not None:
            response_message = util.publish_info(guid, 'prod')
            if response_message['success']:
                await message.answer(response_message['message'])
            else:
                await message.answer(response_message['message']['errorMessage'])
        else:
            await message.answer('GUID продукта указан некорректно.')
    else:
        await message.answer('Публикация сообщения о лицензии, сертификате, доверенности')


@dp.message_handler(commands=['reset'])
async def reset_request_status(message: types.Message):
    if len(message.text.split(' ')) == 2:
        guid = message.text.split(maxsplit=1)[1]
        if re.match(regular_guid, guid) is not None:
            response_message = util.publish_info(guid, 'prod')
            await message.answer(response_message['message'])
        else:
            await message.answer('GUID заявки указан некорректно.')
    else:
        await message.answer('Сбросить заявку со статуса CertRequestCreation (6) в черновик (1).\n'
                             'Зависшая заявка, отсутствует кнопка отправить заявление.')

if __name__ == '__main__':
    executor.start_polling(dp)
