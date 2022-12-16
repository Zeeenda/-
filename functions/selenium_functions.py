import selenium.common.exceptions
import chromedriver_autoinstaller
import asyncio

from selenium import webdriver
from selenium.webdriver.common.by import By


# функция для генерации фото с помощью библиотеки selenium
# через сервис replicate.com/pixray/text2image
async def generate_photo(text):
    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome()
    driver.get("https://replicate.com/pixray/text2image")

    await asyncio.sleep(5)
    driver.find_element(By.NAME, "prompts").send_keys("\b"*42)
    driver.find_element(By.NAME, "prompts").send_keys(text)
    await asyncio.sleep(1)
    driver.find_element(By.CLASS_NAME, "form-button").click()

    # сервис генерирует фото долгое время,
    # чтобы не затягивать ожидание пользователя - сервису даётся 90 секунд
    await asyncio.sleep(90)
    try:
        element = driver.find_elements(By.TAG_NAME, "img")[0]
        return element.get_attribute("src")
    except:
        return None


# функция для генерации продолжения текста с помощью библиотеки selenium
# через сервис балабоба от яндекса yandex.ru/lab/yalm
async def generate_text(text):
    chromedriver_autoinstaller.install()

    driver = webdriver.Chrome()
    driver.get("https://yandex.ru/lab/yalm")
    button = driver.find_element(By.CLASS_NAME, "html-curtain__button")
    button.click()

    driver.find_element(By.CLASS_NAME, "Textarea-Control").send_keys(text)
    driver.find_element(By.CLASS_NAME, "submit_visible").click()
    counter = 0
    while counter != 40:
        try:
            text = driver.find_element(By.CLASS_NAME, "balaboba-response-text-span")\
                .find_element(By.CLASS_NAME, "response__text").get_attribute("innerHTML")
            return text
        except selenium.common.exceptions.NoSuchElementException:
            await asyncio.sleep(1)
            counter += 1

    return None
