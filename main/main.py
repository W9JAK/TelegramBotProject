from telebot import TeleBot, types
from config import my_token, CHANEL_CHAT_ID
import re
from db import update_user_info, add_order, delete_order, get_user_orders, get_user_institution_type, get_services_by_institution_type, get_item_params_by_name_and_type, get_order_details, get_user_username, hide_order, update_order_status
from yookassa import Payment
import uuid
from decimal import Decimal
import random


bot = TeleBot(my_token)


user_data = {}
cart_message_ids = {}


answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', 'Мой разработчик не говорил, что отвечать в такой ситуации... >_<']


# Обрабатывает входящие сообщения и реагирует на команды или текст сообщений.
@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    user_id = message.from_user.id
    if message.text == '/start':
        start(message)
    elif message.text in ['🏛️ Университет/Колледж', '🏫 Школа']:
        choose_education_institution(message)
    elif message.text == '↩️ Вернуться к выбору':
        start(message)
    elif message.text == '📞 Связаться с нами' or message.text == '/contact':
        handle_contact_button(message)
    elif message.text == '📖 Услуги' or message.text == '/services':
        institution_type = get_user_institution_type(user_id)
        goodsChapter(message, institution_type)
    elif message.text == '🛒 Корзина' or message.text == '/cart':
        handle_view_cart(message)
    elif message.text.startswith('📝 Оформить'):
        handle_buy_button(message)
    elif message.text == '↩️ Назад':
        institution_type = get_user_institution_type(user_id)
        goodsChapter(message, institution_type)
    elif message.text == '↩️ Назад в меню' or message.text == '/main_menu':
        main_menu(message)
    elif message.text in ['Дипломная работа', 'Курсовая работа', 'Итоговый доклад', 'Итоговый проект', 'Научная статья', 'Презентация', 'Доклад', 'Практическая работа', 'Уникальная практическая работа', 'Доклад + презентация', 'Сценарий для мероприятий']:
        institution_type = get_user_institution_type(message.from_user.id)
        show_item_info(message, institution_type)
    else:
        bot.send_message(message.chat.id, random.choice(answers))


# Функция для отправки сообщения о том, что услуги для школ не предоставляются
def send_school_message(chat_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("↩️ Вернуться к выбору"))

    bot.send_message(chat_id, "К сожалению, мы пока не предоставляем услуги для школ.", reply_markup=keyboard)


# Отправляет приветственное сообщение и предлагает выбрать образовательное учреждение.
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    university_button = types.KeyboardButton('🏛️ Университет/Колледж')
    school_button = types.KeyboardButton('🏫 Школа')
    markup.add(university_button, school_button)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\n'
                                      f'Вас приветствует компания FreeBies!\n'
                                      f'Здесь ты можешь оформить заказ на наши услуги.\n'
                                      f'Выберите ваше образовательное учреждение:', reply_markup=markup)


# Выбор между видом учебных заведений
@bot.message_handler(func=lambda message: message.text in ['🏛️ Университет/Колледж', '🏫 Школа'])
def choose_education_institution(message):
    user_id = message.from_user.id
    username = message.from_user.username
    institution_type = 'university' if message.text == '🏛️ Университет/Колледж' else 'school'
    update_user_info(user_id, username, institution_type)
    main_menu(message)


# Показывает главное меню бота с доступными опциями.
@bot.message_handler(commands=['main_menu'])
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('📖 Услуги')
    contact_button = types.KeyboardButton('📞 Связаться с нами')
    cart_button = types.KeyboardButton('🛒 Корзина')
    return_button = types.KeyboardButton('↩️ Вернуться к выбору')

    markup.row(button1)
    markup.row(contact_button)
    markup.row(cart_button)
    markup.row(return_button)

    bot.send_message(message.chat.id, 'Перекинул тебя в главное меню!', reply_markup=markup)


# Показывает список доступных услуг или товаров.
def goodsChapter(message, institution_type=None):
    if institution_type is None:
        user_id = message.from_user.id
        institution_type = get_user_institution_type(user_id)

    services = get_services_by_institution_type(institution_type)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for service in services:
        service_button = types.KeyboardButton(service['name'])
        markup.add(service_button)
    markup.add(types.KeyboardButton('↩️ Назад в меню'))
    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:', reply_markup=markup)


# Отправляет сообщение с вариантами связи.
@bot.message_handler(commands=['contact'])
def handle_contact_button(message):
    contact_message = 'Для связи с администратором нажмите кнопку ниже'
    contact_markup = create_contact_options_markup()

    bot.send_message(message.chat.id, contact_message, reply_markup=contact_markup)


# Создает инлайн-клавиатуру с вариантами контактов.
def create_contact_options_markup():
    markup = types.InlineKeyboardMarkup()
    responsible_button = types.InlineKeyboardButton("Связаться с ответственным по заказам", url="https://t.me/AnotherTime3")
    markup.row(responsible_button)

    return markup


# Информирует пользователя об услуге быстро, правильно, надежно.
def bpn(message):
    bot.send_message(message.chat.id, 'Если вы затянули со сроком выполнения работы, то мы сделаем все за вас в крaтчайшие сроки (цена зависит от срока выполнения работы и ее сложности)')
    markup = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton("Связаться с нами", url="https://t.me/AnotherTime3")
    markup.add(contact_button)
    bot.send_message(message.chat.id, 'Для уточнения деталей работы и обсуждения цен, нажмите кнопку ниже:', reply_markup=markup)


# Информирует пользователя об услуге написания лекций.
def show_lectures_info(message):
    bot.send_message(message.chat.id, 'Пропустили учебный день? Нужно написать много лекций? Не беда, наша команда профессионалов специализируется на написании лекций. Не теряйте времени и доверьтесь нам. Свяжитесь с нами уже сегодня, чтобы получить свою лекцию завтра')
    markup = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton("Связаться с нами", url="https://t.me/AnotherTime3")
    markup.add(contact_button)
    bot.send_message(message.chat.id, 'Для уточнения деталей работы и обсуждения цен, нажмите кнопку ниже:', reply_markup=markup)


# Показывает информацию о выбранной услуге или товаре.
def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F" 
                               u"\U0001F300-\U0001F5FF"  
                               u"\U0001F680-\U0001F6FF"  
                               u"\U0001F1E0-\U0001F1FF"  
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               "]+", flags=re.UNICODE)
    return emoji_pattern.sub(r'', text)


# Показывает информацию о выбранной услуге или товаре.
def show_item_info(message, institution_type):
    item_name = remove_emojis(message.text.split(':')[1]).strip() if ':' in message.text else remove_emojis(
        message.text).strip()
    item_params = get_item_params_by_name_and_type(item_name, institution_type)

    if item_params:
        amount = item_params['amount']
        custom_description = item_params.get('custom_description', 'Описание отсутствует')
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton(f'📝 Оформить: {item_name}')
        button2 = types.KeyboardButton('↩️ Назад')
        markup.row(button1, button2)
        item_info = f'Описание: {custom_description}\nСтоимость: {amount} рублей'
        bot.send_message(message.chat.id, item_info, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Услуга не найдена")


# Обрабатывает нажатие кнопки оформления заказа на услугу.
@bot.message_handler(func=lambda message: message.text.startswith('📝 Оформить'))
def handle_buy_button(message):
    user_id = message.from_user.id
    institution_type = get_user_institution_type(user_id)
    item_name = remove_emojis(message.text.split(':')[1]).strip()
    item_params = get_item_params_by_name_and_type(item_name, institution_type)

    if item_params:
        if item_name == "Сценарий для мероприятий":
            ask_for_scenario_option(message, item_params, item_name)
        else:
            proceed_to_speed_up_option(message, item_params, item_name)
    else:
        bot.send_message(message.chat.id, "Товар не найден")


# Добавление кнопок с видами сценариев
def ask_for_scenario_option(message, item_params, item_name):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    options = ['1) Базовый сценарий', '2) Сценарий с презентацией', '3) Подробный сценарий']
    for option in options:
        markup.add(types.KeyboardButton(option))
    markup.add(types.KeyboardButton('↩️ Назад'))
    msg = bot.send_message(message.chat.id, "Выберите вариант сценария:\n1) Общий сценарий на заданную вами тему, без детализации\nСтоимость: 1000 рублей\n2) Общий сценарий на заданную вами тему, презентация, средняя степень детализации в тексте\nСтоимость: 2500 рублей\n3) Общий сценарий на заданную вами тему, подробное описание каждого действия, презентация, высшая степень детализации\nСтоимость: 4000 рублей", reply_markup=markup)

    bot.register_next_step_handler(msg, process_scenario_selection, item_params, item_name)


# Изменение цены в зависимости от вида сценария
def process_scenario_selection(message, item_params, item_name):
    selection = message.text
    institution_type = item_params.get('institution_type')
    if selection == '↩️ Назад':
        goodsChapter(message, institution_type)
    elif selection == '1) Базовый сценарий':
        proceed_to_speed_up_option(message, item_params, item_name)
    elif selection == '2) Сценарий с презентацией':
        item_params['amount'] = 2500
        proceed_to_speed_up_option(message, item_params, item_name)
    elif selection == '3) Подробный сценарий':
        item_params['amount'] = 4000
        proceed_to_speed_up_option(message, item_params, item_name)
    else:
        bot.send_message(message.chat.id, "Неизвестный выбор, пожалуйста, попробуйте снова.")
        ask_for_scenario_option(message, item_params, item_name)


# Создает клавиатуру для выбора ускоренного выполнения работы.
def proceed_to_speed_up_option(message, item_params, item_name):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    acceleration_button = types.KeyboardButton('Ускорение')
    skip_button = types.KeyboardButton('Пропустить')

    if item_name in ['Курсовая работа', 'Дипломная работа', 'Итоговый проект']:
        super_acceleration_button = types.KeyboardButton('Сверхускорение')
        markup.add(super_acceleration_button)
        speed_up_question = (f"Хотите ускорить выполнение работы за дополнительную плату?\n"
                             f"1) Ускорение до {item_params['speed_up_time']} за {item_params['speed_up_amount']} рублей\n"
                             f"2) Сверхускорение до {item_params['super_speed_up_time']} за {item_params['super_speed_up_amount']} рублей")
    else:
        speed_up_question = (f"Хотите ускорить выполнение работы до {item_params['speed_up_time']} "
                             f"за дополнительную плату {item_params['speed_up_amount']} рублей?")

    markup.add(acceleration_button)
    markup.add(skip_button)

    msg = bot.send_message(message.chat.id, speed_up_question, reply_markup=markup)
    bot.register_next_step_handler(msg, process_speed_up_choice, item_params, item_name)


# Обрабатывает выбор пользователя по ускоренному выполнению работы.
def process_speed_up_choice(message, item_params, item_name):
    choice = message.text.lower()
    if choice == 'ускорение':
        item_params['speed_up'] = True
        item_params['amount'] += item_params['speed_up_amount']
        request_education_institution_name(message, item_params, item_name)
    elif choice == 'сверхускорение':
        item_params['speed_up'] = True
        item_params['amount'] += item_params['super_speed_up_amount']
        item_params['speed_up_time'] = item_params['super_speed_up_time']
        request_education_institution_name(message, item_params, item_name)
    elif choice == 'пропустить':
        item_params['speed_up'] = False
        request_education_institution_name(message, item_params, item_name)
    else:
        msg = bot.send_message(message.chat.id, "Не понимаю ваш выбор. Пожалуйста, выберите один из предложенных вариантов.")
        bot.register_next_step_handler(msg, process_speed_up_choice, item_params, item_name)


# Запрашиваем название учебного заведения
def request_education_institution_name(message, item_params, item_id):
    msg = bot.send_message(message.chat.id, "Напишите название вашего учебного заведения:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_education_institution_name, item_params, item_id)


# Вычисляет общую стоимость заказа с учетом дополнительных услуг.
def calculate_total_amount(item_params):
    speed_up_amount = item_params.get('speed_up_amount', 0)
    try:
        speed_up_amount = int(speed_up_amount)
    except ValueError:
        speed_up_amount = 0

    speed_up_selected = item_params.get('speed_up_selected', False)
    speed_up_cost = speed_up_amount if speed_up_selected else 0

    total_amount = item_params.get('amount', 0) + speed_up_cost

    return total_amount


# Обрабатывает ввод названия учебного заведения пользователя.
def process_education_institution_name(message, item_params, item_id):
    item_params['education_institution_name'] = message.text
    msg = bot.send_message(message.chat.id, "Напишите тему работы:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_title, item_params, item_id)


# Обрабатывает ввод темы работы.
def process_project_title(message, item_params, item_id):
    item_params['project_title'] = message.text
    msg = bot.send_message(message.chat.id, "Пришлите файл с методическими указаниями или опишите их:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_description, item_params, item_id)


# Обрабатывает ввод методических указаний или описания работы.
def process_project_description(message, item_params, item_id):
    if message.content_type == 'document':
        item_params['project_description_file_id'] = message.document.file_id
        item_params['file_name'] = message.document.file_name
        item_params['file_size'] = message.document.file_size
        item_params['project_description'] = "Файл с методическими указаниями прикреплен."
    elif message.content_type == 'text':
        item_params['project_description'] = message.text
        item_params['project_description_file_id'] = None

    if item_params.get('name') in ['Итоговый проект', 'Итоговый доклад', 'Курсовая работа', 'Дипломная работа']:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        yes_button = types.KeyboardButton('Да')
        no_button = types.KeyboardButton('Нет')
        markup.add(yes_button, no_button)
        msg = bot.send_message(message.chat.id, "Есть ли у вас содержание работы? В случае его отсутствия мы составим содержание сами за дополнительную плату 300 рублей.", reply_markup=markup)
        bot.register_next_step_handler(msg, process_has_contents, item_params, item_id)
    else:
        msg = bot.send_message(message.chat.id, "Есть ли какие-то пожелания к работе?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_project_requirements, item_params, item_id)


# Запрашивает наличие у пользователя содержания работы.
def process_has_contents(message, item_params, item_id):
    choice = message.text.lower()
    if choice == 'да':
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите содержание работы:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_contents_input, item_params, item_id)
    elif choice == 'нет':
        item_params['amount'] += 300
        item_params['has_contents'] = False
        msg = bot.send_message(message.chat.id, "Есть ли какие-то пожелания к работе?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_project_requirements, item_params, item_id)
    else:
        msg = bot.send_message(message.chat.id, "Не понимаю ваш выбор. Пожалуйста, ответьте 'Да' или 'Нет'.")
        bot.register_next_step_handler(msg, process_has_contents, item_params, item_id)
        return


def process_contents_input(message, item_params, item_id):
    item_params['contents'] = message.text
    item_params['has_contents'] = True
    msg = bot.send_message(message.chat.id, "Есть ли какие-то пожелания к работе?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_requirements, item_params, item_id)


def process_project_requirements(message, item_params, item_id):
    item_params['project_requirements'] = message.text
    ask_source_of_knowledge(message, item_params, item_id)


# Запрашивает у пользователя, откуда он узнал о компании
def ask_source_of_knowledge(message, item_params, item_id):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    markup.add('От селлера', 'Другой вариант')
    msg = bot.send_message(message.chat.id, "Откуда вы узнали о существовании нашей компании?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_source_response, item_params, item_id)


# Обрабатывает ответ пользователя на вопрос об источнике информации
def process_source_response(message, item_params, item_id):
    source = message.text
    if source == 'От селлера':
        msg = bot.send_message(message.chat.id, "Введите промокод:")
        bot.register_next_step_handler(msg, process_promo_code, item_params, item_id)
    elif source == 'Другой вариант':
        msg = bot.send_message(message.chat.id, "Пожалуйста, напишите, откуда вы о нас узнали:")
        bot.register_next_step_handler(msg, process_custom_source, item_params, item_id)
    else:
        msg = bot.send_message(message.chat.id, "Не удалось распознать ваш выбор. Пожалуйста, выберите один из предложенных вариантов: 'От селлера' или 'Другой вариант'.")
        bot.register_next_step_handler(msg, process_source_response, item_params, item_id)


# Обрабатывает ввод промокода пользователем
def process_promo_code(message, item_params, item_id):
    item_params['promo_code'] = message.text
    confirm_order_or_proceed(message, item_params, item_id)


# Обрабатывает ввод пользователем собственного источника информации о компании
def process_custom_source(message, item_params, item_id):
    item_params['source_of_information'] = message.text
    confirm_order_or_proceed(message, item_params, item_id)


# Запрашивает у пользователя подтверждение заказа или возврат в меню
def confirm_order_or_proceed(message, item_params, item_id):
    ask_for_contact_info(message, item_params, item_id)


def ask_for_contact_info(message, item_params, item_id):
    msg = bot.send_message(message.chat.id,
                           "Пожалуйста, укажите ваш дополнительный способ связи (например, телефон, email и т.д.):")
    bot.register_next_step_handler(msg, process_contact_method, item_params, item_id)


def process_contact_method(message, item_params, item_id):
    contact_method = message.text
    item_params['contact_method'] = contact_method
    ask_for_subscription(message, item_params, item_id)


def ask_for_subscription(message, item_params, item_id):
    user_id = message.chat.id
    user_data[user_id] = {'item_params': item_params, 'item_id': item_id}

    markup = types.InlineKeyboardMarkup()
    group_button = types.InlineKeyboardButton("Группа", url="https://t.me/SHg8w")
    subscribe_button = types.InlineKeyboardButton("Подписался", callback_data="check_subscription")
    skip_button = types.InlineKeyboardButton("Пропустить", callback_data="skip_subscription")
    markup.add(group_button, subscribe_button, skip_button)

    bot.send_message(user_id, "Подпишитесь на наш канал, чтобы быть в курсе последних новостей и акций и получить СКИДКУ на заказ в 3%!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["check_subscription", "skip_subscription"])
def handle_subscription_callback(call):
    user_id = call.message.chat.id

    if call.data == "check_subscription":
        check_user_subscription(call)
    elif call.data == "skip_subscription":
        bot.answer_callback_query(call.id, "Вы можете подписаться позже.")
        proceed_after_subscription_check(call.message, user_id)


def check_user_subscription(call):
    user_id = call.from_user.id
    chat_id = "@SHg8w"

    try:
        response = bot.get_chat_member(chat_id, user_id)
        if response.status not in ["left", "kicked"]:
            if user_id in user_data:
                user_data[user_id]['item_params']['subscription_discount_applied'] = True

                current_amount = user_data[user_id]['item_params']['amount']
                discounted_amount = current_amount * Decimal('0.97')
                user_data[user_id]['item_params']['amount'] = discounted_amount

                bot.send_message(call.message.chat.id, "Спасибо за подписку! Вам применена скидка 3%.")
                proceed_after_subscription_check(call.message, user_id)
        else:
            bot.send_message(call.message.chat.id, "Кажется, вы еще не подписались. Пожалуйста, подпишитесь на канал.")
    except Exception as e:
        print(f"Error checking subscription: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка при проверке подписки.", show_alert=True)


def proceed_after_subscription_check(message, user_id):
    if user_id in user_data:
        item_params = user_data[user_id]['item_params']
        item_id = user_data[user_id]['item_id']
        del user_data[user_id]

        confirm_order(message=message, item_params=item_params, item_id=item_id)


def confirm_order(message, item_params, item_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    confirm_button = types.KeyboardButton('Подтвердить заказ')
    change_button = types.KeyboardButton('↩️ Назад в меню')
    markup.add(confirm_button, change_button)
    msg = bot.send_message(message.chat.id, "Желаете подтвердить свой заказ?", reply_markup=markup)
    bot.register_next_step_handler(msg, final_confirmation, item_params, item_id)


# Обрабатывает окончательное подтверждение заказа пользователем.
def final_confirmation(message, item_params, item_id):
    choice = message.text
    if choice == 'Подтвердить заказ':
        user_id = message.from_user.id
        amount = item_params['amount']
        description = item_params['description']
        project_title = item_params.get('project_title', '')
        project_description = item_params.get('project_description', '')
        project_requirements = item_params.get('project_requirements', '')
        speed_up = item_params.get('speed_up', False)
        education_institution_name = item_params.get('education_institution_name', '')
        source_of_information = item_params.get('source_of_information', '')
        promo_code = item_params.get('promo_code', '')
        contact_method = item_params.get('contact_method', '')
        project_description_file_id = item_params.get('project_description_file_id', None)
        file_name = item_params.get('file_name', None)
        file_size = item_params.get('file_size', None)
        institution_type = get_user_institution_type(user_id)
        subscription_discount_applied = item_params.get('subscription_discount_applied', False)

        add_order(user_id, item_id, amount, description, project_title, project_description,
                  project_requirements, speed_up, education_institution_name,
                  item_params.get('has_contents', False), item_params.get('contents', ''), source_of_information, promo_code, contact_method,
                  institution_type, subscription_discount_applied, project_description_file_id, file_name, file_size)

        bot.send_message(message.chat.id, "Ваш заказ подтвержден и добавлен в корзину!", reply_markup=types.ReplyKeyboardRemove())
        handle_view_cart(message)
    elif choice == '↩️ Назад в меню':
        goodsChapter(message)


# Обрабатывает запрос на удаление заказа через callback-запрос от кнопки.
@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_order(call):
    order_id = call.data.split('_')[1]
    delete_order(order_id)

    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text=f"Заказ удален из корзины.")
    bot.answer_callback_query(call.id, f"Заказ удален из корзины.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('hide_'))
def handle_hide_order(call):
    order_id = call.data.split('_')[1]
    hide_order(order_id)
    bot.edit_message_text(chat_id=call.message.chat.id,
                          message_id=call.message.message_id,
                          text="Заказ скрыт из корзины.")
    bot.answer_callback_query(call.id, "Заказ скрыт из корзины.")


# Отображает пользователю содержимое его корзины
@bot.message_handler(commands=['cart'])
def handle_view_cart(message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)

    if user_id in cart_message_ids:
        for msg_id in cart_message_ids[user_id]:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=msg_id)
            except Exception as e:
                print(f"Не удалось удалить сообщение: {str(e)}")
        cart_message_ids[user_id] = []

    if orders:
        message_ids = []
        for order in orders:
            cart_text = create_cart_text(order)
            markup = create_individual_markup(order)
            msg = bot.send_message(message.chat.id, cart_text, reply_markup=markup)
            message_ids.append(msg.message_id)
        cart_message_ids[user_id] = message_ids
    else:
        msg = bot.send_message(message.chat.id, "Ваша корзина пуста.")
        cart_message_ids[user_id] = [msg.message_id]


def create_cart_text(order):
    content_line = f'Содержание: {order["contents"]}\n' if order.get("contents") else ""
    status_line = get_order_status_description(order["order_status"])
    return (
        f'{order["description"]} за {order["amount"]} руб.\n'
        f'Ускоренное выполнение: {"Да" if order["speed_up"] else "Нет"}\n'
        f'Название учебного заведения: {order["education_institution_name"]}\n'
        f'Тема работы: {order["project_title"]}\n'
        f'{content_line}'
        f'Пожелания к работе: {order["project_requirements"]}\n'
        f'Методические указания: {order["project_description"]}\n'
        f'Статус заказа: {status_line}\n'
    )


def create_individual_markup(order):
    markup = types.InlineKeyboardMarkup()
    order_id = order["order_id"]
    order_status = order["order_status"]
    is_partial_payment = order.get('is_partial_payment', False)
    partial_payment_completed = order.get('partial_payment_completed', False)

    if order_status == 0:
        markup.add(types.InlineKeyboardButton(text="Оплатить полностью", callback_data=f'full_{order_id}'))
        if not is_partial_payment:
            markup.add(types.InlineKeyboardButton(text="Оплатить частично", callback_data=f'partial_{order_id}'))
        markup.add(types.InlineKeyboardButton(text="Удалить заказ", callback_data=f"delete_{order_id}"))

    elif order_status == 1:
        markup.add(types.InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/AnotherTime3"))
        markup.add(types.InlineKeyboardButton(text="Отменить заказ", callback_data=f"cancel_order_{order_id}"))

    elif order_status == 2 and not partial_payment_completed:
        markup.add(types.InlineKeyboardButton(text="Оплатить остаток", callback_data=f"pay_remaining_{order_id}"))
        markup.add(types.InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/AnotherTime3"))

    elif order_status == 3:
        markup.add(types.InlineKeyboardButton(text="Оставить отзыв", url="https://t.me/FreeBiesotz"))
        markup.add(types.InlineKeyboardButton(text="Отчистить корзину", callback_data=f"hide_{order_id}"))

    elif order_status == 4:
        markup.add(types.InlineKeyboardButton(text="Связаться с менеджером", url="https://t.me/AnotherTime3"))

    markup.add(types.InlineKeyboardButton(text="Меню", callback_data="back_to_menu"))

    return markup

def get_order_status_description(status_code):
    return {
        0: "Ожидает оплаты",
        1: "Оплачен и выполняется",
        2: "Выполняется и ожидает доплаты",
        3: "Выполнен",
        4: "Обрабатывается доплата"
    }.get(status_code, "Неизвестный статус")


@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_order_'))
def cancel_order(call):
    order_id = call.data.split('_')[2]
    user_id = call.from_user.id
    user_username = get_user_username(user_id)

    admin_message = f"Пользователь @{user_username} (ID: {user_id}) запросил отмену заказа {order_id}."
    markup = types.InlineKeyboardMarkup()
    confirm_cancellation_button = types.InlineKeyboardButton(
        text="Подтвердить отмену",
        callback_data=f"confirm_cancellation_{order_id}_{user_id}"
    )
    markup.add(confirm_cancellation_button)
    bot.send_message(CHANEL_CHAT_ID, admin_message, reply_markup=markup)

    user_message = "Мы получили ваш запрос на отмену заказа. В ближайшее время менеджер свяжется в сами для уточнения деталей."
    bot.send_message(user_id, user_message)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_cancellation_'))
def confirm_cancellation(call):
    parts = call.data.split('_')
    if len(parts) < 4:
        bot.answer_callback_query(call.id, "Некорректные данные для обработки.")
        return

    command, action, order_id, user_id = parts

    try:
        order_id = int(order_id)
    except ValueError:
        bot.answer_callback_query(call.id, "Некорректный идентификатор заказа.")
        return

    delete_order(order_id)

    bot.answer_callback_query(call.id, "Отмена заказа подтверждена.")
    bot.edit_message_text(
        text=f"Отмена заказа {order_id} подтверждена менеджером.",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

    user_message = "Отмена вашего заказа подтверждена менеджером, и он удален из корзины."
    bot.send_message(user_id, user_message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('full_') or call.data.startswith('partial_'))
def process_payment_method(call):
    order_id = call.data.split('_')[1]
    order = get_order_details(order_id)
    amount = order['amount']

    is_partial_payment = call.data.startswith('partial_')
    if is_partial_payment:
        amount /= 2  # Делим сумму на две части для частичной оплаты
        payment_description = "Частичная оплата заказа"
    else:
        payment_description = "Полная оплата заказа"

    payment_url = create_payment(amount, order['description'], order_id, is_partial_payment)

    markup = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton(text="Перейти к оплате", url=payment_url)
    markup.add(pay_button)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"{payment_description}. Нажмите на кнопку для оплаты:",
                          reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('pay_remaining_'))
def handle_remaining_payment(call):
    order_id = call.data.split('_')[2]
    order = get_order_details(order_id)
    remaining_amount = order['amount'] / 2

    payment_url = create_payment(remaining_amount, "Оплата оставшейся части заказа", order_id, is_partial_payment=True)

    markup = types.InlineKeyboardMarkup()
    pay_button = types.InlineKeyboardButton(text="Перейти к оплате", url=payment_url)
    markup.add(pay_button)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text="Пожалуйста, перейдите по ссылке для оплаты оставшейся части заказа:",
                          reply_markup=markup)

    update_order_status(order_id, partial_payment_completed=True)


# Обрабатывает callback-запрос, связанный с возвращением в главное меню
@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def callback_back_to_menu(call):
    bot.answer_callback_query(call.id)
    main_menu(call.message)


def create_payment(amount, description, order_id, is_partial_payment=False):
    return_url = 'https://your-website.com/success-page'
    payment = Payment.create({
        "amount": {
            "value": str(amount),
            "currency": "RUB"
        },
        "confirmation": {
            "type": "redirect",
            "return_url": f"{return_url}?order_id={order_id}"
        },
        "description": description,
        "capture": True,
        "metadata": {
            "order_id": order_id,
            "is_partial_payment": is_partial_payment  # Добавляем флаг частичной оплаты
        }
    }, uuid.uuid4())
    return payment.confirmation.confirmation_url


# Запускает бота и обрабатывает входящие сообщения в бесконечном цикле.
def start_bot():
    bot.polling(none_stop=True)
