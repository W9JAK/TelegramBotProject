import uuid
from yookassa import Payment
import psycopg2
from config import DATABASE_URL
from telebot import TeleBot, types
from config import my_token

bot = TeleBot(my_token)


def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', 'Мой разработчик не говорил, что отвечать в такой ситуации... >_<']


temp_storage = {}


def get_item_params_by_name(name):
    conn = get_db_connection()
    item_params = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, amount, description, custom_description, speed_up_amount, speed_up_time, additional_delivery_cost
                FROM items
                WHERE name = %s
            """, (name,))
            row = cursor.fetchone()
            if row:
                item_params = {
                    'name': row[0],
                    'amount': row[1],
                    'description': row[2],
                    'custom_description': row[3],
                    'speed_up_amount': row[4],
                    'speed_up_time': row[5],
                    'additional_delivery_cost': row[6]
                }
    except Exception as e:
        print(f"Ошибка при получении данных об услуге {name}: {e}")
    finally:
        conn.close()
    return item_params


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == '/start':
        start(message)
    elif message.text in ['🏛️ Университет/Колледж', '🏫 Школа']:
        choose_education_institution(message)
    elif message.text == '📞 Связаться с нами' or message.text == '/contact':
        handle_contact_button(message)
    elif message.text == '📖 Услуги' or message.text == '/services':
        goodsChapter(message)
    elif message.text == '🛒 Корзина' or message.text == '/cart':
        handle_view_cart(message)
    elif message.text.startswith('📝 Оформить'):
        handle_buy_button(message)
    elif message.text == '↩️ Назад':
        goodsChapter(message)
    elif message.text == '↩️ Назад в меню' or message.text == '/main_menu':
        main_menu(message)
    elif message.text == '🆘📚 БПН':
        bpn(message)
    elif message.text == '✏️📔 Лекции':
        show_lectures_info(message)
    elif message.text in ['🎓📚 Дипломная работа', '📘📝 Курсовая работа', '📊📢 Итоговый доклад', '🏆📑 Итоговый проект', '📄🔍 Научная статья']:
        show_item_info(message)
    else:
        bot.send_message(message.chat.id, answers[0])


def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    university_button = types.KeyboardButton('🏛️ Университет/Колледж')
    school_button = types.KeyboardButton('🏫 Школа')
    markup.add(university_button, school_button)
    user_id = message.from_user.id
    username = message.from_user.username
    update_user_info(user_id, username)
    bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\n'
                                      f'Вас приветствует компания StudyHelp!\n'
                                      f'Здесь ты можешь оформить заказ на наши услуги.',
                     reply_markup=markup)
    bot.send_message(message.chat.id, "Выберите ваше образовательное учреждение:", reply_markup=markup)


# Обработчик выбора образовательного учреждения
@bot.message_handler(func=lambda message: message.text in ['Университет/Колледж', 'Школа'])
def choose_education_institution(message):
    if message.text == '🏛️ Университет/Колледж':
        main_menu(message)  # Переходим к приветственному сообщению и меню услуг
    elif message.text == '🏫 Школа':
        bot.send_message(message.chat.id, "К сожалению, мы пока не предоставляем услуги для школ.", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(commands=['main_menu'])
def main_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('📖 Услуги')
    contact_button = types.KeyboardButton('📞 Связаться с нами')
    cart_button = types.KeyboardButton('🛒 Корзина')
    markup.row(button1)
    markup.row(contact_button)
    markup.row(cart_button)
    bot.send_message(message.chat.id, 'Перекинул тебя в главное меню!', reply_markup=markup)


@bot.message_handler(commands=['services'])
def goodsChapter(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    items = ['🎓📚 Дипломная работа', '📘📝 Курсовая работа', '📊📢 Итоговый доклад', '🏆📑 Итоговый проект', '📄🔍 Научная статья', '🆘📚 БПН', '✏️📔 Лекции']
    buttons = [types.KeyboardButton(item) for item in items]
    for button in buttons:
        markup.add(button)
    markup.add(types.KeyboardButton('↩️ Назад в меню'))

    bot.send_message(message.chat.id, 'Вот все товары, которые сейчас находятся в продаже:', reply_markup=markup)


# Функции для связи с ответственным по заказам и с разработчиком бота
@bot.message_handler(commands=['contact'])
def handle_contact_button(message):
    contact_message = 'Выберите, каким способом вы хотите связаться:'
    contact_markup = create_contact_options_markup()

    bot.send_message(message.chat.id, contact_message, reply_markup=contact_markup)


def create_contact_options_markup():
    markup = types.InlineKeyboardMarkup()
    responsible_button = types.InlineKeyboardButton("Связаться с ответственным по заказам", url="https://t.me/gelya200309")
    developer_button = types.InlineKeyboardButton("Связаться с разработчиком бота", url="https://t.me/aagrinin")
    markup.row(developer_button)
    markup.row(responsible_button)

    return markup


# Функция услуги быстро, правильно, надежно
def bpn(message):
    bot.send_message(message.chat.id, 'Если вы затянули со сроком выполнения работы, то мы сделаем все за вас в крaтчайшие сроки (цена зависит от срока выполнения работы и ее сложности)')
    markup = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton("Связаться с нами", url="https://t.me/gelya052004")
    markup.add(contact_button)
    bot.send_message(message.chat.id, 'Для уточнения деталей работы и обсуждения цен, нажмите кнопку ниже:', reply_markup=markup)


def show_lectures_info(message):
    bot.send_message(message.chat.id, 'Пропустили учебный день? Нужно написать много лекций? Не беда, наша команда профессионалов специализируется на написании лекций. Не теряйте времени и доверьтесь нам. Свяжитесь с нами уже сегодня, чтобы получить свою лекцию завтра')
    markup = types.InlineKeyboardMarkup()
    contact_button = types.InlineKeyboardButton("Связаться с нами", url="https://t.me/gelya052004")
    markup.add(contact_button)
    bot.send_message(message.chat.id, 'Для уточнения деталей работы и обсуждения цен, нажмите кнопку ниже:', reply_markup=markup)


def show_item_info(message):
    # Разделяем сообщение на команду и название услуги
    _, item_name = message.text.split(maxsplit=1)
    item_name = item_name.strip()  # Убираем лишние пробелы
    item_params = get_item_params_by_name(item_name)
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


def handle_buy_button(message):
    item_id = message.text.split(':')[1].strip()
    item_params = get_item_params_by_name(item_id)
    if item_params:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        speed_up_question = f'Хотите ускорить выполнение работы до {item_params["speed_up_time"]} за дополнительную плату {item_params["speed_up_amount"]} рублей?'
        yes_button = types.KeyboardButton('Да')
        no_button = types.KeyboardButton('Нет')
        markup.row(yes_button, no_button)
        msg = bot.send_message(message.chat.id, speed_up_question, reply_markup=markup)
        bot.register_next_step_handler(msg, process_speed_up_choice, item_params, item_id)
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
    if 'speed_up' in item_params and item_params['speed_up']:
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
        item_params['speed_up'] = True
        item_params['amount'] += item_params['speed_up_amount']
    elif choice == 'нет':
        item_params['speed_up'] = False
    else:
        bot.send_message(message.chat.id, "Выберите, пожалуйста, 'Да' или 'Нет'.")
        return  # Выход, чтобы предотвратить продолжение в случае неправильного ввода
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    courier_question = 'Хотите доставку курьером за дополнительную плату 500 рублей?'
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')
    markup.row(yes_button, no_button)
    msg = bot.send_message(message.chat.id, courier_question, reply_markup=markup)
    bot.register_next_step_handler(msg, process_delivery_choice, item_params, item_id)


def process_delivery_choice(message, item_params, item_id):
    choice = message.text.lower()
    if choice in ['да', 'нет']:
        item_params['courier_delivery'] = choice == 'да'
        if item_params['courier_delivery']:
            item_params['amount'] += 500
        msg = bot.send_message(message.chat.id, "Напишите название вашего учебного заведения:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_education_institution_name, item_params, item_id)
    else:
        bot.send_message(message.chat.id, "Выберите, пожалуйста, 'Да' или 'Нет'.")


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


def update_user_info(user_id, username):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET username = EXCLUDED.username;
            """, (user_id, username))
        conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении информации пользователя {user_id}: {e}")
    finally:
        conn.close()


def get_user_username(user_id):
    conn = get_db_connection()
    username = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT username FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                username = result[0]
    except Exception as e:
        print(f"Ошибка при получении username пользователя {user_id}: {e}")
    finally:
        conn.close()
    return username


def process_education_institution_name(message, item_params, item_id):
    item_params['education_institution_name'] = message.text
    msg = bot.send_message(message.chat.id, "Напишите тему работы:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_title, item_params, item_id)

def process_project_title(message, item_params, item_id):
    item_params['project_title'] = message.text
    msg = bot.send_message(message.chat.id, "Пришлите методические указания или опишите их:", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_description, item_params, item_id)

def process_project_description(message, item_params, item_id):
    item_params['project_description'] = message.text
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    yes_button = types.KeyboardButton('Да')
    no_button = types.KeyboardButton('Нет')
    markup.add(yes_button, no_button)
    msg = bot.send_message(message.chat.id, "Есть ли у вас содержание работы? В случае его отсутвия мы составим содержание сами за дополнительную плату 300 рублей", reply_markup=markup)
    bot.register_next_step_handler(msg, process_has_contents, item_params, item_id)


def process_has_contents(message, item_params, item_id):
    choice = message.text.lower()
    if choice == 'да':
        msg = bot.send_message(message.chat.id, "Пожалуйста, введите содержание работы:", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_contents_input, item_params, item_id)
    elif choice == 'нет':
        item_params['amount'] += 300  # Увеличиваем цену на 300 рублей
        item_params['has_contents'] = False
        msg = bot.send_message(message.chat.id, "Есть ли какие-то пожелания к работе?", reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_project_requirements, item_params, item_id)
    else:
        msg = bot.send_message(message.chat.id,"Не понимаю ваш выбор. Пожалуйста, ответьте 'Да' или 'Нет'.")
        bot.register_next_step_handler(msg, process_has_contents, item_params, item_id)
        return


def process_contents_input(message, item_params, item_id):
    item_params['contents'] = message.text
    item_params['has_contents'] = True
    msg = bot.send_message(message.chat.id, "Есть ли какие-то пожелания к работе?", reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, process_project_requirements, item_params, item_id)


def process_project_requirements(message, item_params, item_id):
    item_params['project_requirements'] = message.text
    confirm_order_or_proceed(message, item_params, item_id)


def confirm_order_or_proceed(message, item_params, item_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    confirm_button = types.KeyboardButton('Подтвердить заказ')
    change_button = types.KeyboardButton('↩️ Назад в меню')
    markup.add(confirm_button, change_button)
    msg = bot.send_message(message.chat.id, "Желаете подтвердить свой заказ?", reply_markup=markup)
    bot.register_next_step_handler(msg, final_confirmation, item_params, item_id)


def final_confirmation(message, item_params, item_id):
    choice = message.text
    if choice == 'Подтвердить заказ':
        user_id = message.from_user.id
        amount = item_params['amount']
        description = item_params['description']
        delivery_selected = item_params.get('courier_delivery', False)
        project_title = item_params.get('project_title', '')
        project_description = item_params.get('project_description', '')
        project_requirements = item_params.get('project_requirements', '')
        speed_up = item_params.get('speed_up', False)
        courier_delivery = item_params.get('courier_delivery', False)
        education_institution_name = item_params.get('education_institution_name', '')

        add_order(user_id, item_id, amount, description, delivery_selected, project_title, project_description,
                  project_requirements, speed_up, courier_delivery, education_institution_name,
                  item_params.get('has_contents', False), item_params.get('contents', ''))

        bot.send_message(message.chat.id, "Ваш заказ подтвержден и добавлен в корзину!", reply_markup=types.ReplyKeyboardRemove())
        handle_view_cart(message)
    elif choice == '↩️ Назад в меню':
        goodsChapter(message)


@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_'))
def handle_edit_order(call):
    order_id = call.data.split('_')[1]
    # Сохраняем order_id во временное хранилище, чтобы использовать его в последующих шагах редактирования
    temp_storage[call.from_user.id] = {'order_id': order_id}
    bot.send_message(call.message.chat.id, "Введите новую тему работы:")
    bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_new_project_title, call.from_user.id)

def process_new_project_title(message, user_id):
    new_title = message.text
    # Получаем order_id из временного хранилища
    order_id = temp_storage[user_id]['order_id']
    temp_storage[user_id]['project_title'] = new_title
    # Запрашиваем следующие данные
    bot.send_message(message.chat.id, "Введите новое описание работы:")
    bot.register_next_step_handler(message, process_new_project_description, user_id)

def process_new_project_description(message, user_id):
    new_description = message.text
    temp_storage[user_id]['project_description'] = new_description
    # Запрашиваем последние данные
    bot.send_message(message.chat.id, "Введите новые требования к работе:")
    bot.register_next_step_handler(message, process_new_project_requirements, user_id)

def process_new_project_requirements(message, user_id):
    new_requirements = message.text
    # Обновляем данные в базе данных
    order_id = temp_storage[user_id]['order_id']
    update_order_details(order_id, temp_storage[user_id]['project_title'], temp_storage[user_id]['project_description'], new_requirements)
    bot.send_message(message.chat.id, "Детали заказа обновлены.")
    handle_view_cart(message)


def update_order_details(order_id, project_title, project_description, project_requirements):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE orders
                SET project_title = %s, project_description = %s, project_requirements = %s
                WHERE order_id = %s
            """, (project_title, project_description, project_requirements, order_id))
            conn.commit()
    except Exception as e:
        print("Ошибка при обновлении деталей заказа:", e)
    finally:
        conn.close()


# Добавление заказа в базу данных с message_id
def add_order(user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents))
            conn.commit()
    except Exception as e:
        print("Ошибка при добавлении заказа:", e)
    finally:
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
                          text=f"Заказ удален из корзины.")
    bot.answer_callback_query(call.id, f"Заказ удален из корзины.")


def get_user_orders(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    orders = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents
                FROM orders
                WHERE user_id = %s
            """, (user_id,))
            orders = [{
                'order_id': row[0],
                'user_id': row[1],
                'item_id': row[2],
                'amount': row[3],
                'description': row[4],
                'delivery_selected': row[5],
                'project_title': row[6],
                'project_description': row[7],
                'project_requirements': row[8],
                'speed_up': row[9],
                'courier_delivery': row[10],
                'education_institution_name': row[11],
                'has_contents': row[12],
                'contents': row[13]
            } for row in cursor.fetchall()]
    except Exception as e:
        print("Ошибка при получении заказов пользователя:", e)
    finally:
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


@bot.message_handler(commands=['cart'])
def handle_view_cart(message):
    user_id = message.from_user.id
    orders = get_user_orders(user_id)
    if orders:
        for order in orders:
            speed_up_text = "Да" if order['speed_up'] else "Нет"
            courier_delivery_text = "Да" if order['courier_delivery'] else "Нет"
            contents_text = order['contents'] if order['has_contents'] else "Нет"
            order_details = f'{order["description"]} за {order["amount"]} рублей\n' \
                            f'Название учебного заведения: {order["education_institution_name"]}\n' \
                            f'Тема работы: {order["project_title"]}\n' \
                            f'Методические указания: {order["project_description"]}\n' \
                            f'Содержание: {contents_text}\n' \
                            f'Пожелания к работе: {order["project_requirements"]}\n' \
                            f'Ускоренное выполнение: {speed_up_text}\n' \
                            f'Курьерская доставка: {courier_delivery_text}'
            payment_link = create_payment(order["amount"], order["description"], order["order_id"])
            markup = types.InlineKeyboardMarkup()
            pay_button = types.InlineKeyboardButton(text="Оплатить", url=payment_link)
            delete_button = types.InlineKeyboardButton(text="Удалить", callback_data=f"delete_{order['order_id']}")
            edit_button = types.InlineKeyboardButton(text="Редактировать", callback_data=f"edit_{order['order_id']}")
            menu_button = types.InlineKeyboardButton(text="Меню", callback_data="back_to_menu")
            markup.add(pay_button, delete_button, menu_button)
            markup.add(edit_button)
            bot.send_message(message.chat.id, order_details, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Ваша корзина пуста.")


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def callback_back_to_menu(call):
    bot.answer_callback_query(call.id)
    main_menu(call.message)

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
            "return_url": return_url  # Удалено добавление order_id в URL
        },
        "metadata": {
            "order_id": str(order_id)  # Явное добавление order_id в метаданные платежа
        },
        "description": description
    }, uuid.uuid4())  # Использование uuid.uuid4() для генерации уникального идентификатора платежа
    return payment.confirmation.confirmation_url


def start_bot():
    bot.polling(none_stop=True)


if __name__ == '__main__':
    start_bot()
