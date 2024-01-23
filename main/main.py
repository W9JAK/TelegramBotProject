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
Configuration.account_id = get_from_env("SHOP_ID")
Configuration.secret_key = get_from_env("PAYMENT_TOKEN")


bot = telebot.TeleBot(my_token)
answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', 'Мой разработчик не говорил, что отвечать в такой ситуации... >_<']


def get_item_params_by_id(item_id):
    items_data = {
        'Дипломная работа': {'amount': 25000, 'description': 'Дипломная работа', 'custom_description': 'Дипломная работа - это финальная работа студента, которую он выполняет в конце обучения в высшем учебном заведении. Дипломная работа позволяет студенту продемонстрировать полученные знания и умения в выбранной области и провести исследование или практическую работу по конкретной теме\nCрок выполнения: до 7 дней', 'speed_up_amount': '', 'speed_up_time': '3 дней'},
        'Курсовая работа': {'amount': 6000, 'description': 'Курсовая работа', 'custom_description': 'Курсовая работа -это научно-исследовательская работа, которую студенты выполняют в рамках учебного курса. Она является одним из основных видов контроля знаний студента в учебном заведении. Курсовая работа предполагает самостоятельное изучение определенной темы, проведение исследований, анализ и обработку полученных данных, а также написание научного текста, содержащего выводы и рекомендации по изучаемой проблематике. Благодаря нашему сервису вы получите первоклассную работу с высокой оригинальностью.\nCрок выполнения: до 3 дней', 'speed_up_amount': 1500, 'speed_up_time': '1 дня'},
        'Итоговая докладная': {'amount': 4000, 'description': 'Итоговая докладная', 'custom_description': 'Итоговый доклад -это работа в котором подводятся итоги работы или проекта. В нём включаются основные достижения, проблемы, накопленный опыт, рекомендации и планы на будущее. Данная работа создается с целью показать результаты работы или проекта, оценить их эффективность и влияние на достижение поставленных целей.\nCрок выполнения: до 4 дней', 'speed_up_amount': '', 'speed_up_time': '1 дня'},
        'Итоговый проект': {'amount': 3000, 'description': 'Итоговый проект', 'custom_description': 'Итоговый проект – это работа или задание, выполняемое в конце учебного в целях проверки и оценки знаний, навыков и компетенций, которые ученик или студент приобрел в течение обучения.\nCрок выполнения: до 3 дней', 'speed_up_amount': '', 'speed_up_time': '1 дня'},
        'Научная статья': {'amount': 2000, 'description': 'Научная статья', 'custom_description': 'Научная статья - это работа, в которой представлены результаты научного исследования. Она содержит подробное описание проблемы, цели исследования, методологии, полученных данных и анализа. Научная статья также включает обсуждение результатов, их интерпретацию, выводы и рекомендации для дальнейших исследований. Зачастую, такие работы, публикуется в научных журналах и доступна для ознакомления другими учеными и специалистами в той же области знания.\nCрок выполнения: до 3 дней', 'speed_up_amount': 1000, 'speed_up_time': '1 дня'},
    }

    item_params = items_data.get(item_id)
    return item_params


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == '/start':
        welcome(message)
    elif message.text == '📞 Связаться с нами':
        handle_contact_button(message)
    elif message.text == '📖 Услуги':
        goodsChapter(message)
    elif message.text.startswith('💳 Купить'):
        handle_buy_button(message)
    elif message.text == '↩️ Назад':
        goodsChapter(message)
    elif message.text == '↩️ Назад в меню':
        welcome(message)
    elif message.text == '🆘📚 БПН':
        bpn(message)
    elif message.text == '✏️📔 Лекции':
        show_lectures_info(message)
    elif message.text in ['КУБГТУ', 'КУБГМУ', 'КУБГУ', 'ККИРУК', 'ИМСИТ']:
        handle_university_selection(message)
    elif message.text in ['🎓📚 Дипломная работа', '📘📝 Курсовая работа', '📊📢 Итоговая докладная', '🏆📑 Итоговый проект', '📄🔍 Научная статья']:
        show_item_info(message)
    else:
        bot.send_message(message.chat.id, answers[0])


def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('📖 Услуги')
    contact_button = types.KeyboardButton('📞 Связаться с нами')

    markup.row(button1)
    markup.row(contact_button)

    if message.text == '/start':
        # Use the send_message function to send a text message with the keyboard markup
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\n'
                                          f'Вас приветствует компания StudyHelp!\n'
                                          f'Здесь ты можешь оформить заказ на наши услуги.',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Перекинул тебя в главном меню! Выбирай!', reply_markup=markup)


def goodsChapter(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = ['🎓📚 Дипломная работа', '📘📝 Курсовая работа', '📊📢 Итоговая докладная', '🏆📑 Итоговый проект', '📄🔍 Научная статья', '🆘📚 БПН', '✏️📔 Лекции']
    buttons = [types.KeyboardButton(item) for item in items]
    for button in buttons:
        markup.add(button)
    markup.add(types.KeyboardButton('↩️ Назад в меню'))

    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:', reply_markup=markup)


# Функции для связи с ответственным по заказам и с разработчиком бота
def handle_contact_button(message):
    contact_message = 'Выберите, каким способом вы хотите связаться:'
    contact_markup = create_contact_options_markup()

    bot.send_message(message.chat.id, contact_message, reply_markup=contact_markup)


def create_contact_options_markup():
    markup = types.InlineKeyboardMarkup()
    responsible_button = types.InlineKeyboardButton("Связаться с ответственным по заказам", url="https://t.me/s1erben1")
    developer_button = types.InlineKeyboardButton("Связаться с разработчиком бота", url="https://t.me/aagrinin")
    markup.row(developer_button)
    markup.row(responsible_button)

    return markup


# Функция услуги (любые задания, личное обсуждение)
def bpn(message):
    bot.send_message(message.chat.id, 'Если вы затянули со сроком выполнения работы, то мы сделаем все за вас в крaтчайшие сроки (цена зависит от срока выполнения работы и ее сложности)')
    markup = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton("Связаться с нами", url="https://t.me/aagrinin")
    markup.add(contact_button)
    bot.send_message(message.chat.id, 'Для уточнения деталей работы и обсуждения цен, нажмите кнопку ниже:', reply_markup=markup)


# Функции, связанные с лекциями
def show_lectures_info(message):
    service_description = "Пропустили учебный день? Нужно написать много лекций? Не беда, наша команда профессионалов специализируется на написании лекций. Не теряйте времени и доверьтесь нам. Свяжитесь с нами уже сегодня, чтобы получить свою лекцию завтра"
    bot.send_message(message.chat.id, service_description)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    universities = ['КУБГТУ', 'КУБГМУ', 'КУБГУ', 'ККИРУК', 'ИМСИТ']
    university_buttons = [types.KeyboardButton(university) for university in universities]
    university_buttons.append(types.KeyboardButton('↩️ Назад'))
    markup.add(*university_buttons)

    bot.send_message(message.chat.id, 'Выберите ваш университет:', reply_markup=markup)


def handle_university_selection(message):
    selected_university = message.text
    bot.send_message(message.chat.id, f'Вы выбрали {selected_university} для связи со специалистом.')
    contact_url = get_contact_url_for_university(selected_university)
    contact_button = types.InlineKeyboardButton("Связаться с нами", url=contact_url)
    reply_markup = types.InlineKeyboardMarkup().add(contact_button)

    bot.send_message(message.chat.id, 'Нажмите кнопку ниже, чтобы связаться со специалистом:', reply_markup=reply_markup)


def get_contact_url_for_university(university):
    # Replace with actual usernames or URLs for each university.
    university_contacts = {
        'КУБГТУ': 'https://t.me/aagrinin',
        'КУБГМУ': 'https://t.me/s1erben1',
        'КУБГУ': 'https://t.me/Vou4ok',
        'ККИРУК': 'https://t.me/gwcbdur91752p2p',
        'ИМСИТ': 'https://t.me/aagrinin',
    }
    return university_contacts.get(university, '')


# Функция информация для оплаты
def show_item_info(message):
    item_id = message.text.split(maxsplit=1)[1].strip()
    item_params = get_item_params_by_id(item_id)
    if item_params:
        amount, description, custom_description = item_params['amount'], item_params['description'], item_params.get('custom_description')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(f'💳 Купить: {item_id}')
        button2 = types.KeyboardButton('↩️ Назад')
        markup.row(button1, button2)
        item_info = f'Информация об услуге {item_id}:\nОписание: {custom_description}\nСтоимость: {amount} рублей'
        bot.send_message(message.chat.id, item_info, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Товар не найден")


# Фунуции кнопка оплаты (обычная, ускоренная)
def handle_buy_button(message):
    item_id = message.text.split(':')[1].strip()
    item_params = get_item_params_by_id(item_id)

    if item_params:
        description = item_params['description']
        speed_up_amount = item_params.get('speed_up_amount', 0)
        speed_up_time = item_params.get('speed_up_time', 0)

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes_button = types.KeyboardButton('Да')
        no_button = types.KeyboardButton('Нет')
        back_button = types.KeyboardButton('↩️ Назад')
        markup.row(yes_button, no_button)
        markup.row(back_button)

        bot.send_message(message.chat.id,
                         f'Хотите ускорить выполнение работы до {speed_up_time} для "{description}" за дополнительную плату {speed_up_amount} рублей?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, process_speed_up_choice, item_params, item_id)
    else:
        bot.send_message(message.chat.id, "Товар не найден")


def create_speed_up_markup(item_params, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')

    markup.row(yes_button, no_button)
    markup.row(types.KeyboardButton('↩️ Назад'))  # Add a back button

    item_id = item_params.get('description', '')
    bot.register_next_step_handler(message, process_speed_up_choice, item_params, item_id)
    return markup


def create_delivery_markup(item_params, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')

    markup.row(yes_button, no_button)
    markup.row(types.KeyboardButton('↩️ Назад'))  # Add a back button

    # Проверяем, было ли выбрано ускорение
    if 'speed_up_selected' in item_params and item_params['speed_up_selected']:
        # Если ускорение было выбрано, предлагаем доставку курьером
        item_id = item_params.get('description', '')  # Используем 'description' вместо 'id'
        bot.register_next_step_handler(message, process_delivery_choice, item_params, item_id)
    else:
        # Если ускорение не было выбрано, переходим к оплате
        process_delivery_choice(message, item_params, None)  # Изменяем item_id на None

    return markup


def process_speed_up_choice(message, item_params, item_id):
    choice = message.text.lower()
    description = item_params['description']
    additional_delivery_cost = 500

    # Проверяем, является ли speed_up_amount числом
    try:
        speed_up_amount = int(item_params.get('speed_up_amount', 0))
    except (ValueError, TypeError):
        speed_up_amount = 0

    if choice == 'да':
        item_params['speed_up_selected'] = True
    elif choice == 'нет':
        item_params['speed_up_selected'] = False
    elif choice == 'назад':
        handle_buy_button(message)
        return
    else:
        goodsChapter(message)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')
    back_button = types.KeyboardButton('↩️ Назад')
    markup.row(yes_button, no_button)
    markup.row(back_button)

    bot.send_message(message.chat.id,
                     f"За дополнительную плату {additional_delivery_cost} рублей хотите получить распечатанную работу курьером?",
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_delivery_choice, item_params, item_id)


def process_delivery_choice(message, item_params, item_id):
    choice = message.text.lower()
    description = item_params['description']
    additional_delivery_cost = 500

    # Проверяем, является ли speed_up_amount числом
    try:
        speed_up_amount = int(item_params.get('speed_up_amount', 0))
    except (ValueError, TypeError):
        speed_up_amount = 0

    # Проверяем, было ли выбрано ускорение
    if 'speed_up_selected' in item_params and item_params['speed_up_selected']:
        # Если ускорение было выбрано, предлагаем доставку курьером
        if choice == 'да':
            item_params['delivery_selected'] = True
            amount = item_params.get('amount', 0) + additional_delivery_cost + speed_up_amount
        elif choice == 'нет':
            item_params['delivery_selected'] = False
            amount = item_params.get('amount', 0) + speed_up_amount
        elif choice == 'назад':
            process_speed_up_choice(message, item_params, item_id)
            return
        else:
            goodsChapter(message)
            return
    else:
        # Если ускорение не было выбрано, просто переходим к выбору доставки курьером
        if choice == 'да':
            item_params['delivery_selected'] = True
            amount = item_params.get('amount', 0) + additional_delivery_cost
        elif choice == 'нет':
            item_params['delivery_selected'] = False
            amount = item_params.get('amount', 0)
        elif choice == 'назад':
            process_speed_up_choice(message, item_params, item_id)
            return
        else:
            goodsChapter(message)
            return

    payment_url = payment_for_item(amount, description, item_id, message.chat.id)
    reply_markup = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton("Оплатить", url=payment_url)
    reply_markup.add(pay_button)

    bot.send_message(message.chat.id, f"Итоговая сумма с учетом дополнительной платы: {amount} рублей\n"
                                      f"Для оплаты перейдите по ссылке:", reply_markup=reply_markup)


# Функция для создания платежа
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


bot.polling(none_stop=True)
