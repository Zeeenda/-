from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


# функция возвращает стандартную клавиатуру со всеми функциями бота
def default_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton(text="узнать погоду")
    b2 = KeyboardButton(text="Балабоба от Яндекса")
    b3 = KeyboardButton(text="текст в фото с помощью ИИ")
    b4 = KeyboardButton(text="проверка файла через VirusTotal")
    kb.add(b1, b2)
    kb.row(b3)
    kb.add(b4)

    return kb


# клавиатура содержащая кнопку "отменить"
def get_cancel():
    return ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton("отменить"))
