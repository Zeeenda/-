import asyncio

from aiogram import Dispatcher
from handlers.user import register_user
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from bot_loader import bot
from db import create_table

# инициализируем базу данных SQLite3 и создаём в ней таблицу для хранения городов
# если её не существует
create_table()


# регистрируем обработки комманд от пользователя
def register_all_handlers(dispatcher):
    register_user(dispatcher)


async def main():
    # создаём хранилище
    storage = MemoryStorage()
    # создаём диспетчер бота, бот берётся из bot_loader.py
    dp = Dispatcher(bot, storage=storage)

    register_all_handlers(dp)

    # start
    try:
        # запускаем бота в режиме polling
        await dp.start_polling()

    finally:
        await dp.storage.close()
        await dp.storage.wait_closed()
        await bot.session.close()


if __name__ == '__main__':
    try:
        # асинхронно
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped!")
