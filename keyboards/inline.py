from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

cities = ["Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург",
          "Казань", "Нижний Новгород", "Челябинск", "Самара"]


def weather_menu():
    ikb = InlineKeyboardMarkup(row_width=1)
    b1 = InlineKeyboardButton(text="узнать погоду⛅",
                              callback_data="get_weather")
    b2 = InlineKeyboardButton(text="изменить город🏙️",
                              callback_data="change_city")
    ikb.add(b1, b2)
    return ikb


def get_back():
    ikb = InlineKeyboardMarkup(row_width=1)
    b1 = InlineKeyboardButton(text="назад ↩", callback_data="back")

    ikb.add(b1)
    return ikb


def get_cities():
    ikb = InlineKeyboardMarkup(row_width=2)

    for city in cities:
        ikb.insert(InlineKeyboardButton(text=city, callback_data=city))

    back = InlineKeyboardButton(text="назад ↩", callback_data="back")
    ikb.add(back)

    return ikb


def generate_link_ikb(link):
    ikb = InlineKeyboardMarkup()
    b1 = InlineKeyboardButton('ссылка на анализ', url=link)
    ikb.add(b1)
    return ikb
