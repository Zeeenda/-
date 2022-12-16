import os

from aiogram import Bot
from dotenv import load_dotenv

# получаем значение параметра BOT_TOKEN из файла .env и сохраняем её
# в переменную bot_token
load_dotenv()
bot_token = os.getenv('BOT_TOKEN')

# создаём экземпляр бота
bot = Bot(token=bot_token, parse_mode='HTML')
