import os
import uuid

from aiogram import Dispatcher
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from functions.selenium_functions import generate_photo, generate_text
from db import city_get, city_set
from functions.other import get_weather_info, VirusTotal
from keyboards.reply import default_keyboard, get_cancel
from keyboards.inline import weather_menu, get_back, get_cities, cities, \
    generate_link_ikb
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from bot_loader import bot


# класс описывающий состояние ввода пользователем данных
class InputStates(StatesGroup):
    text_to_photo = State()
    text_to_text = State()
    change_city = State()
    wait_file = State()


# срабатывает при /start
async def user_start(message: Message):
    await message.answer("выберите, что вы хотите сделать:",
                         reply_markup=default_keyboard())


# срабатывает если сообщение от пользователя не попало ни в один из обработчиков
async def any_message(message: Message, state: FSMContext = None):
    if await state.get_state():
        await message.answer("некорректный ввод. отправьте требуемый тип", reply_markup=get_cancel())
    else:
        await message.answer(
            "воспользуйтесь кнопками для использования функций бота:",
            reply_markup=default_keyboard())


# перевод в состояние ввода текста для последующей обработки в фото с помощью ИИ
async def text_to_photo(message: Message):
    await InputStates.text_to_photo.set()
    await message.answer("отправьте текст НА АНГЛИЙСКОМ:",
                         reply_markup=get_cancel())


# перевод в состояние ввода текста для последующей обработки балабобой
async def text_to_text(message: Message):
    await InputStates.text_to_text.set()
    await message.answer("отправьте текст:",
                         reply_markup=get_cancel())


# меню погоды
async def weather(message: Message):
    city = city_get(message.from_user.id)
    if not city:
        await message.answer(f"город не указан. По умолчанию выбрано: Москва",
                             reply_markup=weather_menu())
    else:
        await message.answer(f"выбран город: {city}",
                             reply_markup=weather_menu())


# обработка кнопки - Изменить город
async def change_city_query(callback: CallbackQuery):
    await callback.message.edit_text("выберите город. "
                                     "чтобы ввести город не из списка, "
                                     "воспользуйтесь командой\n/change_city",
                                     reply_markup=get_cities())


# обработка выбора города с помощью предложенных вариантов в виде кнопки
async def change_city_select(callback: CallbackQuery):
    city_set(callback.from_user.id, callback.data)
    await callback.answer("город изменён!")
    await back_to_weather(callback)


# обработка команды /change_city и перевод в состояние ввода города
async def change_city(message: Message):
    await InputStates.change_city.set()
    await message.answer("введите название города:", reply_markup=get_cancel())


# полученный ввод завершает состояние ввода города и проверяет
# на существование такого города
async def change_city_input(message: Message, state: FSMContext):
    await state.finish()
    new_city = message.text
    info = get_weather_info(new_city)

    # если функция get_weather_info не вернула информацию, а вернула None,
    # значит города скорее всего не существует

    # если город есть:
    if info:
        city_set(message.from_user.id, new_city)
        await message.answer("город установлен!\n\n" + info,
                             reply_markup=get_back())

    # если города нет:
    else:
        await message.answer("некорректно введён город.\n\nвыберите город. "
                             "чтобы ввести город не из списка, "
                             "воспользуйтесь командой /change_city",
                             reply_markup=get_cities())


# обработка кнопки "Назад ↩" в погоде
async def back_to_weather(callback: CallbackQuery):
    message = callback.message
    city = city_get(callback.from_user.id)
    if not city:
        await message.edit_text(
            f"город не указан. по умолчанию выбрано: Москва",
            reply_markup=weather_menu())
    else:
        await message.edit_text(f"выбран город: {city}",
                                reply_markup=weather_menu())


# обработка кнопки "Узнать погоду⛅"
# принцип работы - использование API сервиса openweathermap
async def get_weather(callback: CallbackQuery):
    # функция city_get реализована через базу данных sqlite3, если
    # у пользователя указан город - то он возвращается, в противном случае - None
    city = city_get(callback.from_user.id)
    if city:
        info = get_weather_info(city)
    else:
        # если город у пользователя не указан - по умолчанию отображается
        # погода для Москвы
        city = "Москва"
        info = get_weather_info(city)

    # если произошла ошибка сервера, откуда берётся значение погоды
    if not info:
        info = "произошла ошибка. попробуйте позже."

    # присылается не новое сообщение с информацией о погоде,
    # а изменяется текущее с помощью метода edit_text
    await callback.message.edit_text(info, reply_markup=get_back())


# обработка вводимого значения пользователем для балабобы
# завершается состояние ввода.
async def selenium_balaboba(message: Message, state: FSMContext):
    msg = await message.answer("загрузка...", reply_markup=default_keyboard())
    await state.finish()

    # запускаем генерацию текста на основе введённого.
    # получение данных идёт через парсинг с помощью библеотеки selenium
    # - автоматизацией данных в браузере
    text = await generate_text(message.text)
    # удаляем сообщение "Загрузка..." после получения текста от балабобы
    await msg.delete()

    # если текст найден - он выводится, иначе - сообщение об ошибке
    if text:
        await message.answer(message.text + '\n' + text,
                             reply_markup=default_keyboard())
    else:
        await message.answer(
            "извините, Балабоба не может придумать такой текст :(",
            reply_markup=default_keyboard())


# обработка введённого текста для генерации фото, принцип работы аналогичен
# с балабобой
async def selenium_crayon(message: Message, state: FSMContext):
    msg = await message.answer("загрузка... 2 минутки..",
                               reply_markup=default_keyboard())
    await state.finish()
    photo_link = await generate_photo(message.text)
    await msg.delete()
    await bot.send_photo(chat_id=message.from_user.id, photo=photo_link,
                         reply_markup=default_keyboard())


# обработка кнопки "Отмена" при активном состоянии ввода
async def cancel_state(message: Message, state: FSMContext):
    await message.answer("действие отменено", reply_markup=default_keyboard())
    await state.finish()


# переход в состояние ожидания файла для VirusTotal
async def virustotal(message: Message):
    await message.answer("отправьте файл:", reply_markup=get_cancel())
    await InputStates.wait_file.set()


# Загрузка и получение анализе о файле с помощью VirusTotal API
async def virustotal_get_file(message: Message, state: FSMContext):
    await state.finish()
    await message.answer("загрузка файла на VirtusTotal...",
                         reply_markup=default_keyboard())
    file_id = message.document.file_id
    file = await bot.get_file(file_id)

    if len(message.document.file_name.split(".")) >= 2:
        file_extension = '.' + message.document.file_name.split(".")[-1]
    else:
        file_extension = ''

    # генерируем уникальное название файла с помощью UUID4
    file_path = 'temp/' + str(uuid.uuid4()) + file_extension
    # скачиваем присланнный пользователем файл
    await bot.download_file(file.file_path, file_path)

    # отправляем файл на загрузку и анализ в VirtusTotal
    # функция вернёт
    # 1. краткую информацию об анализе
    # 2. ссылку на анализ
    # 3. подробную информацию об анализе
    info = await VirusTotal.get_info(file_path)
    # удаляем отправленный пользователем файл
    os.remove(file_path)

    # если вернулись данные, а не None, то пользователь отчёт
    if info:
        if len(info) == 3:
            # генерируем название файла с отчётом
            report_path = 'temp/' + str(uuid.uuid4()) + '.txt'
            # записываем в подробный отчёт полученные данные с анализа
            with open(report_path, "w+", encoding='utf-8') as f:
                f.write(info[2])

            caption = "отчёт о проверке:" + '\n\n' + info[0]
            # отправляем пользователю все данные о проверке
            await message.reply_document(open(report_path, 'rb'),
                                         caption=caption,
                                         reply_markup=generate_link_ikb(
                                             info[1]))
            # удаляем файл с подробным отчётом
            os.remove(report_path)

    else:
        await message.reply("произошла ошибка. попробуйте позже.",
                            reply_markup=default_keyboard())


# регистрация всех обработчиков ввода
def register_user(dp: Dispatcher):
    dp.register_message_handler(user_start, commands=["start"], state="*")

    dp.register_message_handler(cancel_state, Text(equals="отменить"),
                                state=InputStates.text_to_photo)

    dp.register_message_handler(cancel_state, Text(equals="отменить"),
                                state=InputStates.text_to_text)

    dp.register_message_handler(cancel_state, Text(equals="отменить"),
                                state=InputStates.change_city)

    dp.register_message_handler(cancel_state, Text(equals="отменить"),
                                state=InputStates.wait_file)

    dp.register_message_handler(virustotal,
                                Text(equals="проверка файла через VirusTotal"))

    dp.register_message_handler(virustotal_get_file, content_types=["document"],
                                state=InputStates.wait_file)

    dp.register_message_handler(text_to_photo,
                                Text(equals="текст в фото с помощью ИИ"))

    dp.register_message_handler(text_to_text,
                                Text(equals="Балабоба от Яндекса"))

    dp.register_message_handler(weather, Text(equals="узнать погоду"))

    dp.register_message_handler(selenium_balaboba,
                                (lambda message: message.text is not None),
                                state=InputStates.text_to_text)

    dp.register_message_handler(selenium_crayon,
                                (lambda message: message.text is not None),
                                state=InputStates.text_to_photo)

    dp.register_message_handler(change_city_input,
                                (lambda message: message.text is not None),
                                state=InputStates.change_city)

    dp.register_callback_query_handler(change_city_query, (lambda callback_query: callback_query.data == "change_city"))

    dp.register_callback_query_handler(get_weather, (lambda callback_query: callback_query.data == "get_weather"))

    dp.register_callback_query_handler(change_city_select, (lambda callback_query: callback_query.data in cities))

    dp.register_callback_query_handler(back_to_weather, (lambda callback_query: callback_query.data == "back"))

    dp.register_message_handler(change_city, commands=["change_city"])

    dp.register_message_handler(any_message, state='*', content_types=["document", "text", "audio", "photo"])
