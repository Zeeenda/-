import asyncio
import requests
import datetime
import json

# API Токены
WEATHER_TOKEN = "91b7a702f6fab0a699155060f81fac82"
VIRTUSTOTAL_TOKEN = "607f8469bf354417efb50131086fae892c6634b944a63190e29b31af4456e360"


# возвращает информацию о погоде города, который передан в аргумент функции
# либо None при ошибке(например если город не найден)
# реализовано через API сервиса openweathermap.org
def get_weather_info(city):
    code_to_smile = {
        "Clear": "Ясно \U00002600",
        "Clouds": "Облачно \U00002601",
        "Rain": "Дождь \U00002614",
        "Drizzle": "Дождь \U00002614",
        "Thunderstorm": "Гроза \U000026A1",
        "Snow": "Снег \U0001F328",
        "Mist": "Туман \U0001F32B"
    }

    try:
        r = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_TOKEN}&units=metric"
        )
        data = r.json()

        cur_weather = data["main"]["temp"]

        weather_description = data["weather"][0]["main"]
        if weather_description in code_to_smile:
            wd = code_to_smile[weather_description]
        else:
            wd = "Не удалось определить тип погоды :("

        humidity = data["main"]["humidity"]
        pressure = data["main"]["pressure"]
        wind = data["wind"]["speed"]
        sunrise_timestamp = datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])
        sunset_timestamp = datetime.datetime.fromtimestamp(
            data["sys"]["sunset"])
        length_of_the_day = datetime.datetime.fromtimestamp(
            data["sys"]["sunset"]) - datetime.datetime.fromtimestamp(
            data["sys"]["sunrise"])

        month = datetime.datetime.now().month
        if month == 12 or month == 1 or month == 2:
            time_of_year_emoji = "❄️"
        elif 3 <= month <= 5:
            time_of_year_emoji = "🌷"
        elif 6 <= month <= 8:
            time_of_year_emoji = "🌞"
        else:
            time_of_year_emoji = "🍁"

        info = (f"Погода в городе {city}:\n\n"
                f"Температура: {cur_weather}C° {time_of_year_emoji} {wd}\n"
                f"Влажность: {humidity}%\n"
                f"Давление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                f"Восход солнца: {sunrise_timestamp}\n"
                f"Закат солнца: {sunset_timestamp}\n"
                f"Продолжительность дня: {length_of_the_day}\n"
                )
        return info

    except KeyError:
        return None


# класс для загрузки файла на VirtusTotal и получения данных об анализе
# реализовано через API сервиса virustotal.com
class VirusTotal:
    # метод для загрузки файла
    @staticmethod
    async def upload(file_path):
        api_url = 'https://www.virustotal.com/vtapi/v2/file/scan'
        params = dict(apikey=VIRTUSTOTAL_TOKEN)
        with open(file_path, 'rb') as file:
            files = dict(file=(file_path, file))
            response = requests.post(api_url, files=files, params=params)
        if response.status_code == 200:
            result = response.json()
            print("UPLOAD: ", json.dumps(result, sort_keys=False, indent=4))
            return result["scan_id"]

    # метод для получения данных о файле, вызывает метод загрузки файла
    @staticmethod
    async def get_info(file_path):
        api_url = 'https://www.virustotal.com/vtapi/v2/file/report'
        await asyncio.sleep(1)
        resource = await VirusTotal.upload(file_path)
        resource = resource.split('-')[0]
        params = dict(apikey=VIRTUSTOTAL_TOKEN,
                      resource=resource)
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            result = response.json()

            counter = 0
            while counter != 120:
                if result["response_code"] == 1:
                    break
                else:
                    await asyncio.sleep(15)
                    counter += 15
                    response = requests.get(api_url, params=params)
                    if response.status_code == 200:
                        result = response.json()
                    print("response" + str(response))
                    print(json.dumps(result, sort_keys=False, indent=4))

            if result["response_code"] != 1:
                return None

            report = ''
            for key in result['scans']:
                key = key
                detected = ('  Detected: ' + str(result['scans'][key]['detected']))
                version = ('  Version: ' + result['scans'][key]['version'])
                update = ('  Update: ' + result['scans'][key]['update'])
                if result['scans'][key]['result']:
                    results = ('  result: ' + result['scans'][key]['result'])
                else:
                    results = ''

                report += key + '\n' + detected + '\n' + version + '\n' + update + '\n' + results
            short_info = "Всего задействовано антивирусов: " + \
                         str(result["total"]) + '\n' + 'Из них нашли вирус: ' + \
                         str(result["positives"]) + '\n' + \
                         "Хэш файла(md5): " + result["md5"] + '\n'

            link = result["permalink"]
            return [short_info, link, report]
        else:
            return None
