import uuid
import telebot
from telebot import types
from yookassa import Configuration, Payment
from dotenv import load_dotenv
import os
from os.path import join, dirname
import psycopg2


#Получаем данные оплаты и токен из файла
def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


my_token = get_from_env("TELEGRAM_BOT_TOKEN")
Configuration.account_id = get_from_env("SHOP_ID")
Configuration.secret_key = get_from_env("PAYMENT_TOKEN")
DATABASE_URL = get_from_env("DATABASE_URL")


bot = telebot.TeleBot(my_token)
answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', 'Мой разработчик не говорил, что отвечать в такой ситуации... >_<']


#Данные об услугах
def get_item_params_by_id(item_id):
    items_data = {
        'Дипломная работа': {'amount': 25000, 'description': 'Дипломная работа', 'custom_description': 'Дипломная работа - это финальная работа студента, которую он выполняет в конце обучения в высшем учебном заведении. Дипломная работа позволяет студенту продемонстрировать полученные знания и умения в выбранной области и провести исследование или практическую работу по конкретной теме\nCрок выполнения: до 7 дней', 'speed_up_amount': 1, 'speed_up_time': '3 дней'},
        'Курсовая работа': {'amount': 6000, 'description': 'Курсовая работа', 'custom_description': 'Курсовая работа -это научно-исследовательская работа, которую студенты выполняют в рамках учебного курса. Она является одним из основных видов контроля знаний студента в учебном заведении. Курсовая работа предполагает самостоятельное изучение определенной темы, проведение исследований, анализ и обработку полученных данных, а также написание научного текста, содержащего выводы и рекомендации по изучаемой проблематике. Благодаря нашему сервису вы получите первоклассную работу с высокой оригинальностью.\nCрок выполнения: до 3 дней', 'speed_up_amount': 1500, 'speed_up_time': '1 дня'},
        'Итоговая докладная': {'amount': 4000, 'description': 'Итоговая докладная', 'custom_description': 'Итоговый доклад -это работа в котором подводятся итоги работы или проекта. В нём включаются основные достижения, проблемы, накопленный опыт, рекомендации и планы на будущее. Данная работа создается с целью показать результаты работы или проекта, оценить их эффективность и влияние на достижение поставленных целей.\nCрок выполнения: до 4 дней', 'speed_up_amount': 1, 'speed_up_time': '1 дня'},
        'Итоговый проект': {'amount': 3000, 'description': 'Итоговый проект', 'custom_description': 'Итоговый проект – это работа или задание, выполняемое в конце учебного в целях проверки и оценки знаний, навыков и компетенций, которые ученик или студент приобрел в течение обучения.\nCрок выполнения: до 3 дней', 'speed_up_amount': 1, 'speed_up_time': '1 дня'},
        'Научная статья': {'amount': 2000, 'description': 'Научная статья', 'custom_description': 'Научная статья - это работа, в которой представлены результаты научного исследования. Она содержит подробное описание проблемы, цели исследования, методологии, полученных данных и анализа. Научная статья также включает обсуждение результатов, их интерпретацию, выводы и рекомендации для дальнейших исследований. Зачастую, такие работы, публикуется в научных журналах и доступна для ознакомления другими учеными и специалистами в той же области знания.\nCрок выполнения: до 3 дней', 'speed_up_amount': 1000, 'speed_up_time': '1 дня'},
    }

    item_params = items_data.get(item_id)
    item_params['additional_delivery_cost'] = 500
    return item_params


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == '/start':
        welcome(message)
    elif message.text == '📞 Связаться с нами':
        handle_contact_button(message)
    elif message.text == '📖 Услуги':
        goodsChapter(message)
    elif message.text == '🛒 Корзина':
        handle_view_cart(message)
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


#Приветсвенное сообщение
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('📖 Услуги')
    contact_button = types.KeyboardButton('📞 Связаться с нами')
    cart_button = types.KeyboardButton('🛒 Корзина')

    markup.row(button1)
    markup.row(contact_button)
    markup.row(cart_button)

    if message.text == '/start':
        # Use the send_message function to send a text message with the keyboard markup
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\n'
                                          f'Вас приветствует компания StudyHelp!\n'
                                          f'Здесь ты можешь оформить заказ на наши услуги.',
                         reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Перекинул тебя в главном меню! Выбирай!', reply_markup=markup)


#Вывод всех услуг
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


# Функция услуги быстро, правильно, надежно
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

        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        yes_button = types.KeyboardButton('Да')
        no_button = types.KeyboardButton('Нет')
        back_button = types.KeyboardButton('↩️ Назад')
        markup.row(yes_button, no_button)
        markup.row(back_button)

        bot.send_message(message.chat.id,
                         f'Хотите ускорить выполнение работы для "{description}" за дополнительную плату {item_params["speed_up_amount"]} рублей?',
                         reply_markup=markup)
        bot.register_next_step_handler(message, process_speed_up_choice, item_params, item_id)
    else:
        bot.send_message(message.chat.id, "Товар не найден")


# Функция для создания клавиатуры выбора ускоренного выполнения
def create_speed_up_markup(item_params, message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')

    markup.row(yes_button, no_button)
    markup.row(types.KeyboardButton('↩️ Назад'))  # Add a back button

    item_id = item_params.get('description', '')
    bot.register_next_step_handler(message, process_speed_up_choice, item_params, item_id)
    return markup


# Функция для создания клавиатуры выбора доставки
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


# Функция для обработки выбора пользователя по ускоренному выполнению
def process_speed_up_choice(message, item_params, item_id):
    choice = message.text.lower()

    if choice == 'да':
        item_params['speed_up_selected'] = True
        item_params['amount'] += int(item_params['speed_up_amount'])  # Увеличиваем стоимость
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
                     f'Хотите доставку курьером за дополнительную плату 500 рублей?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_delivery_choice, item_params, item_id)


def process_delivery_choice(message, item_params, item_id):
    choice = message.text.lower()

    if choice == 'да':
        item_params['delivery_selected'] = True
        item_params['amount'] += 500  # Увеличиваем стоимость на стоимость доставки
    elif choice == 'нет':
        item_params['delivery_selected'] = False
    elif choice == 'назад':
        process_speed_up_choice(message, item_params, item_id)
        return
    else:
        goodsChapter(message)
        return

    handle_cart_options_final(message, item_params, item_id)


# Функция для обработки выбора пользователя по курьерской доставке
def process_courier_choice(message, item_params, item_id):
    choice = message.text.lower()

    if choice == 'да':
        item_params['courier_delivery_selected'] = True
        item_params['amount'] += 500  # Увеличиваем стоимость
    elif choice == 'нет':
        item_params['courier_delivery_selected'] = False
    elif choice == 'назад':
        process_delivery_choice(message, item_params, item_id)
        return
    else:
        goodsChapter(message)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_to_cart_button = types.KeyboardButton('Добавить в корзину')
    back_button = types.KeyboardButton('↩️ Назад')
    markup.row(add_to_cart_button)
    markup.row(back_button)

    total_amount = calculate_total_amount(item_params)
    bot.send_message(message.chat.id,
                     f'Итоговая цена: {total_amount} рублей\nДобавить в корзину?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, handle_cart_options_final, item_params, item_id)


def calculate_total_amount(item_params):
    # Учитываем стоимость ускоренного выполнения только если выбрано "да"
    speed_up_amount = item_params.get('speed_up_amount', 0)
    try:
        speed_up_amount = int(speed_up_amount)
    except ValueError:
        speed_up_amount = 0

    speed_up_selected = item_params.get('speed_up_selected', False)
    speed_up_cost = speed_up_amount if speed_up_selected else 0

    # Учитываем стоимость курьерской доставки только если выбрано "да"
    courier_delivery_selected = item_params.get('courier_delivery_selected', False)
    additional_delivery_cost = 500 if courier_delivery_selected else 0

    # Подсчет общей суммы
    total_amount = item_params.get('amount', 0) + speed_up_cost + additional_delivery_cost
    return total_amount


def handle_cart_options_final(message, item_params, item_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_to_cart_button = types.KeyboardButton('Добавить в корзину')
    back_button = types.KeyboardButton('↩️ Назад')
    markup.row(add_to_cart_button)
    markup.row(back_button)

    bot.send_message(message.chat.id,
                     f'Итоговая цена: {item_params["amount"]} рублей\n'
                     'Добавить в корзину?',
                     reply_markup=markup)
    bot.register_next_step_handler(message, handle_final_cart_decision, item_params, item_id)


def handle_final_cart_decision(message, item_params, item_id):
    choice = message.text.lower()

    if choice == 'добавить в корзину':
        user_id = message.from_user.id
        if item_params:
            # Отправка сообщения о заказе
            order_message = bot.send_message(message.chat.id, 'Заказ оформлен. Ожидайте подтверждения.')
            # Получение ID отправленного сообщения
            message_id = order_message.message_id
            # Добавление заказа в БД
            add_order(user_id, item_id, item_params['amount'], item_params['description'], item_params.get('delivery_selected', False), message_id)
            bot.send_message(message.chat.id, 'Товар успешно добавлен в корзину!')
        else:
            bot.send_message(message.chat.id, 'Произошла ошибка при добавлении товара в корзину.')
        welcome(message)
    elif choice == 'назад':
        process_delivery_choice(message, item_params, item_id)
    else:
        goodsChapter(message)

def confirm_order(message, amount, description):
    # Отправляем сообщение с подтверждением заказа и кнопкой "Добавить в корзину"
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    add_to_cart_button = types.KeyboardButton('Добавить в корзину')
    back_to_menu_button = types.KeyboardButton('↩️ Назад в меню')
    markup.row(add_to_cart_button)
    markup.row(back_to_menu_button)

    bot.send_message(message.chat.id, f"Итоговая сумма заказа: {amount} рублей\n"
                                      f"Опция доставки: {'Да' if message.chat.order_params['delivery_selected'] else 'Нет'}\n"
                                      f"Хотите добавить этот товар в корзину?", reply_markup=markup)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Добавление заказа в базу данных с message_id
def add_order(user_id, item_id, amount, description, delivery_selected, message_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("""
            INSERT INTO orders (user_id, item_id, amount, description, delivery_selected, message_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, item_id, amount, description, delivery_selected, message_id))
        conn.commit()
    conn.close()


# Получение message_id по order_id
def get_message_id_by_order_id(order_id):
    conn = get_db_connection()
    message_id = None
    with conn.cursor() as cursor:
        cursor.execute("SELECT message_id FROM orders WHERE order_id = %s", (order_id,))
        result = cursor.fetchone()
        if result:
            message_id = result[0]
    conn.close()
    return message_id


# Удаление заказа из базы данных
def delete_order(order_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
    conn.close()


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_order(call):
    order_id = call.data.split('_')[1]
    delete_order(order_id)

    # Обновляем текст сообщения, убирая информацию о заказе и ссылку на оплату
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Заказ {order_id} удален из корзины.")
    bot.answer_callback_query(call.id, f"Заказ {order_id} удален из корзины.")


def get_user_orders(user_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s", (user_id,))
        orders = cursor.fetchall()
    conn.close()
    return orders


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_order_'))
def callback_query(call):
    order_id = call.data.split('_')[2]
    delete_order(order_id)  # Удаление заказа из базы данных

    # Обновление сообщения, чтобы убрать информацию о заказе
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Заказ удалён.")


@bot.message_handler(func=lambda message: message.text == '🛒 Корзина')
def handle_view_cart(message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)
    if orders:
        for order in orders:
            payment_link = create_payment(order[3], order[4], order[0])  # amount, description, order_id
            markup = types.InlineKeyboardMarkup()
            pay_button = types.InlineKeyboardButton(text="Оплатить", url=payment_link)
            delete_button = types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_{order[0]}")
            markup.add(pay_button, delete_button)
            bot.send_message(message.chat.id, f'Заказ {order[0]}: {order[4]} за {order[3]} рублей', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")


# Функция для создания платежа
def create_payment(amount, description, order_id):
    return_url = 'https://your-website.com/success-page'  # URL, на который пользователь будет перенаправлен после оплаты
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{return_url}?order_id={order_id}"
        },
        "description": description
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url


bot.polling(none_stop=True)
