import logging
import os
from pprint import pprint

import requests

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from telebot import TeleBot, types

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - [%(levelname)s] - %(name)s - '
           '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
    handlers=[
        # Логи будут записываться в файл program.log
        logging.FileHandler("program.log"),
        logging.StreamHandler()  # Логи также будут выводиться в консоль
    ]
)
logger = logging.getLogger(__name__)
logger.debug('Начало работы бота')

secret_token = os.getenv('TELEGRAM_TOKEN')
bot = TeleBot(token=secret_token)

URL = 'https://api.thecatapi.com/v1/images/search'

URL_HOROSCOPE = {'Стрелец': 'https://www.thevoicemag.ru/horoscope/daily/sagittarius/',
                 'Овен': 'https://www.thevoicemag.ru/horoscope/daily/aries/',
                 'Телец': 'https://www.thevoicemag.ru/horoscope/daily/taurus/',
                 'Близнецы': 'https://www.thevoicemag.ru/horoscope/daily/gemini/',
                 'Рак': 'https://www.thevoicemag.ru/horoscope/daily/cancer/',
                 'Лев': 'https://www.thevoicemag.ru/horoscope/daily/leo/',
                 'Дева': 'https://www.thevoicemag.ru/horoscope/daily/virgo/',
                 'Весы': 'https://www.thevoicemag.ru/horoscope/daily/libra/',
                 'Дева': 'https://www.thevoicemag.ru/horoscope/daily/virgo/',
                 'Скорпион': 'https://www.thevoicemag.ru/horoscope/daily/scorpio/',
                 'Козерог': 'https://www.thevoicemag.ru/horoscope/daily/capricorn/',
                 'Водолей': 'https://www.thevoicemag.ru/horoscope/daily/aquarius/',
                 'Рыбы': 'https://www.thevoicemag.ru/horoscope/daily/pisces/',
                 }



def get_new_image():
    try:
        response = requests.get(URL)
    except Exception as error:
        logging.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)

    response = response.json()
    random_cat = response[0].get('url')
    return random_cat


@bot.message_handler(commands=['Котик'])
def new_cat(message):
    chat = message.chat
    bot.send_photo(chat.id, get_new_image())


@bot.message_handler(commands=['Гороскоп'])
def horoscope(message):
    chat = message.chat
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    for sign, url in URL_HOROSCOPE.items():
        button_sign = types.KeyboardButton(sign)
        keyboard.add(button_sign)

    bot.send_message(chat.id, text='Выберите свой знак зодиака:', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in URL_HOROSCOPE.keys())
def get_specific_horoscope(message):
    chat = message.chat
    sign = message.text
    url = URL_HOROSCOPE.get(sign)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    description_text = soup.find('div', class_='sign__description-text').text

    bot.send_message(chat.id, f"{sign}:\n{description_text}")

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_back = types.KeyboardButton('/Назад')
    keyboard.add(button_back)

    bot.send_message(chat.id, text='Нажмите "Назад", чтобы вернуться в главное меню', reply_markup=keyboard)


@bot.message_handler(commands=['start'])
def wake_up(message):
    # print(message)
    chat = message.chat
    name = chat.first_name
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_newcat = types.KeyboardButton('/Котик')
    button_horoscope = types.KeyboardButton('/Гороскоп')
    keyboard.add(button_newcat)
    keyboard.add(button_horoscope)

    bot.send_message(
        chat_id=chat.id,
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашёл',
        reply_markup=keyboard,
    )

    bot.send_photo(chat.id, get_new_image())


@bot.message_handler(commands=['Назад'])
def back_to_main_menu(message):
    chat = message.chat
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_newcat = types.KeyboardButton('/Котик')
    button_horoscope = types.KeyboardButton('/Гороскоп')
    keyboard.add(button_newcat)
    keyboard.add(button_horoscope)

    bot.send_message(
        chat_id=chat.id,
        text='Вы вернулись в главное меню',
        reply_markup=keyboard,
    )

@bot.message_handler(content_types=['text'])
def say_hi(message):
    chat = message.chat
    chat_id = chat.id
    bot.send_message(chat_id=chat_id, text='Привет, я БотикБегемотик!')


def main():
    bot.polling()


if __name__ == '__main__':
    main()
