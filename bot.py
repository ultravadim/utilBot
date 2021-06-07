import re
import config
from util.methods import Method

from aiogram import Bot, Dispatcher, executor, types

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher(bot)
re_guid = '[a-zA-Z0-9]{8}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{4}-[a-zA-Z0-9]{12}'
util = Method()


@dp.message_handler(commands=['start', 'help'])
async def welcome_message(message: types.Message):
    await message.answer('Welcome Message')


@dp.message_handler(commands=['mail'])
async def get_mail(message: types.Message):
    if len(message.text.split(' ')) == 2:
        guid = message.text.split(maxsplit=1)[1]
        if re.match(re_guid, guid) is not None:
            response_message = util.mail(guid, 'prod')
            if response_message['success']:
                
                await message.answer(response_message['message']['email'])
            else:
                await message.answer(response_message['message'])
        else:
            pass
    else:
        pass

if __name__ == '__main__':
    executor.start_polling(dp)
