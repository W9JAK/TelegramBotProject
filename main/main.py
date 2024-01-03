import telebot
from telebot import types
from yookassa import Configuration, Payment
from dotenv import load_dotenv
import os
from os.path import join, dirname


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


my_token = get_from_env("TELEGRAM_BOT_TOKEN")
bot = telebot.TeleBot(my_token)
answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', 'Мой разработчик не говорил, что отвечать в такой ситуации... >_<']


Configuration.account_id = get_from_env("SHOP_ID")
Configuration.secret_key = get_from_env("PAYMENT_TOKEN")


# Словарь с параметрами товаров
def get_item_params_by_id(item_id):
    items_data = {
        'Диплом': {'amount': 200, 'description': 'Услуга по написанию дипломной работы'},
        'Лекции': {'amount': 150, 'description': 'Услуга по написанию лекций'},
        'Курс': {'amount': 100, 'description': 'Услуга по созданию курсовой работы'},
        'ИТ. Док': {'amount': 120, 'description': 'Услуга по написанию IT-документации'},
        'ИТ. Проект': {'amount': 180, 'description': 'Услуга по разработке IT-проекта'},
        'Марат': {'amount': 250, 'description': 'Услуга от Марата'},
        'Научн. ст.': {'amount': 120, 'description': 'Услуга по написанию научной статьи'},
    }

    item_params = items_data.get(item_id)
    return item_params


# Обработка кнопки "💳 Купить"
@bot.message_handler(func=lambda message: message.text.startswith('💳 Купить'))
def buy_button_handler(message):
    # Извлекаем идентификатор товара из текста кнопки
    item_id = message.text.split(':')[1].strip()

    # Получаем параметры товара
    item_params = get_item_params_by_id(item_id)
    if item_params:
        amount, description = item_params['amount'], item_params['description']
        payment_url = payment_for_item(amount, description, item_id, message.chat.id)
        bot.send_message(message.chat.id, f"Для оплаты товара '{description}' перейдите по ссылке: {payment_url}")
    else:
        bot.send_message(message.chat.id, "Товар не найден")


# Обработка команды /start
@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🛍 Услуги')
    button2 = types.KeyboardButton('⚙️ Настройки')
    button3 = types.KeyboardButton('📄 Справка')
    markup.row(button1)
    markup.row(button2, button3)

    if message.text == '/start':
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nВас приветствует компания StudyHelp!\nЗдесь ты можешь оформить заказ на наши услуги\nКонтакт ответственного по заказам: https://t.me/aagrinin', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Перекинул тебя в главном меню! Выбирай!', reply_markup=markup)


# Обработка команды "🛍 Услуги"
@bot.message_handler(func=lambda message: message.text == '🛍 Услуги')
def goodsChapter(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('🔹 Диплом')
    button2 = types.KeyboardButton('🔹 Лекции')
    button3 = types.KeyboardButton('🔹 Курс')
    button4 = types.KeyboardButton('🔹 ИТ. Док')
    button5 = types.KeyboardButton('🔹 ИТ. Проект')
    button6 = types.KeyboardButton('🔹 Марат')
    button7 = types.KeyboardButton('🔹 Научн. ст.')
    button8 = types.KeyboardButton('↩️ Назад в меню')
    markup.row(button1, button2)
    markup.row(button3, button4)
    markup.row(button5, button6)
    markup.row(button7, button8)

    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:', reply_markup=markup)


# Обработка кнопки "🔹 Диплом"
@bot.message_handler(func=lambda message: message.text == '🔹 Диплом')
def diploma_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: Диплом')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация о услуге "Диплом":\nСтоимость: 200 рублей', reply_markup=markup)


# Обработка кнопки "🔹 Научн. ст."
@bot.message_handler(func=lambda message: message.text == '🔹 Лекции')
def scientific_article_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: Лекции')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация о услуге "Лекции":\nСтоимость: 150 рублей', reply_markup=markup)


# Обработка кнопки "🔹 Курс"
@bot.message_handler(func=lambda message: message.text == '🔹 Курс')
def course_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: Курс')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация о услуге "Курс":\nСтоимость: 100 рублей', reply_markup=markup)


# Обработка кнопки "🔹 ИТ. Док"
@bot.message_handler(func=lambda message: message.text == '🔹 ИТ. Док')
def it_document_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: ИТ. Док')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация об услуге "ИТ. Документация":\nСтоимость: 120 рублей', reply_markup=markup)


# Обработка кнопки "🔹 ИТ. Проект"
@bot.message_handler(func=lambda message: message.text == '🔹 ИТ. Проект')
def it_project_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: ИТ. Проект')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация об услуге "ИТ. Проект":\nСтоимость: 180 рублей', reply_markup=markup)


# Обработка кнопки "🔹 Марат"
@bot.message_handler(func=lambda message: message.text == '🔹 Марат')
def marat_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: Марат')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация об услуге "Услуга от Марата":\nСтоимость: 250 рублей', reply_markup=markup)


# Обработка кнопки "🔹 Научн. ст."
@bot.message_handler(func=lambda message: message.text == '🔹 Научн. ст.')
def scientific_work_info(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('💳 Купить: Научн. ст.')
    button2 = types.KeyboardButton('↩️ Назад')
    markup.row(button1, button2)

    bot.send_message(message.chat.id, 'Информация об услуге "Научная статья":\nСтоимость: 120 рублей', reply_markup=markup)


# Функция для обработки платежа для конкретного товара
def payment_for_item(amount, description, item_id, chat_id):
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"https://your-website.com/success-page?chat_id={chat_id}&item_id={item_id}"
        },
        "description": description
    })

    payment_url = payment.confirmation.confirmation_url
    return payment_url


# Строчка, чтобы программа не останавливалась
bot.polling(none_stop=True)
