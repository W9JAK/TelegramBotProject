from flask import Flask, request, jsonify
from datetime import datetime
from main import bot
from config import CHANEL_CHAT_ID
from db import get_order_details, get_user_username, update_order_status, get_user_id_by_order_id, fetch_compilation_time
from telebot import types


app = Flask(__name__)


@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    data = request.json
    print("Получены данные webhook:", data)
    if data.get('event') == 'payment.succeeded':
        order_id = data['object']['metadata'].get('order_id')
        if not order_id:
            print("В метаданных платежа отсутствует order_id.")
            return jsonify({'status': 'error', 'message': 'Отсутствует order_id'}), 400

        order = get_order_details(order_id)
        if not order:
            print(f"Информация о заказе с ID {order_id} не найдена.")
            return jsonify({'status': 'error', 'message': 'Детали заказа не найдены'}), 404

        user_id = order['user_id']
        user_username = get_user_username(user_id)
        compilation_time = fetch_compilation_time(order['description'], order['institution_type'], order['speed_up'])
        payment_time = datetime.now().strftime('%H:%M:%S %Y-%m-%d')
        content_line = f'Содержание: {order["contents"]}\n' if order.get("contents") else ""
        payment_type = "Частичная оплата" if order['is_partial_payment'] else "Полная оплата"

        if order['is_partial_payment']:
            if not order['partial_payment_completed']:
                update_order_status(order_id, partial_payment_completed=True, order_status=2)
                user_message = "Ваш заказ был успешно оплачен и взят в работу, ожидайте пока менеджер пришлет вам работу. Вы можете просматривать статус заказа в корзине. Спасибо за доверие!"
                bot.send_message(CHANEL_CHAT_ID, f"Поступила первая часть оплаты заказа {order_id}.")
            else:
                update_order_status(order_id, partial_payment_completed=True, order_status=3)
                user_message = "Вторая часть оплаты успешно завершена. Менеджер свяжется с вами в ближайшее время, чтобы отправить демоверсию работы."
                bot.send_message(CHANEL_CHAT_ID, f"Поступила вторая часть оплаты заказа {order_id}.")
                bot.send_message(user_id, user_message)
                return jsonify({'status': 'success'})
        else:
            update_order_status(order_id, partial_payment_completed=False, order_status=1)
            user_message = "Ваш заказ был успешно оплачен и взят в работу. Вы можете просматривать статус заказа в корзине. Спасибо за доверие!"
            bot.send_message(CHANEL_CHAT_ID, f"Поступила полная оплата заказа {order_id}.")

        try:
            bot.send_message(user_id, user_message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

        send_detailed_admin_message(order, user_username, compilation_time, payment_time, content_line, payment_type, order_id)

    return jsonify({'status': 'success'})


def send_detailed_admin_message(order, user_username, compilation_time, payment_time, content_line, payment_type, order_id):
    detailed_message_to_admin = (
        f'Номер заказа {order["order_id"]}\n'
        f'{order["description"]} за {order["amount"]} рублей\n'
        f'Время на выполнение: до {compilation_time}\n'
        f'Ускоренное выполнение: {"Да" if order["speed_up"] else "Нет"}\n'
        f'Вид учебного заведения: {order["institution_type"]}\n'
        f'Название учебного заведения: {order["education_institution_name"]}\n'
        f'Тема работы: {order["project_title"]}\n'
        f'Методические указания: {order["project_description"]}\n'
        f'{content_line}'
        f'Пожелания к работе: {order["project_requirements"]}\n'
        f'Время оплаты: {payment_time}\n'
        f'ID заказчика: {order["user_id"]}\n'
        f'Доп. способ связи: {order["contact_method"]}\n'
        f'Оплата: {payment_type}\n'
    )

    if order.get("promo_code"):
        detailed_message_to_admin += f'Промокод: {order["promo_code"]}\n'
    else:
        detailed_message_to_admin += f'Откуда узнали: {order.get("source_of_information", "Не указано")}\n'

    if user_username:
        detailed_message_to_admin += f'Заказчик: @{user_username}\n'
    else:
        detailed_message_to_admin += f'Информация о аккаунте тг заказчика недоступна.\n'

    markup = types.InlineKeyboardMarkup()
    complete_button = types.InlineKeyboardButton("Заказ выполнен", callback_data=f"complete_order_{order_id}")
    markup.add(complete_button)
    bot.send_message(CHANEL_CHAT_ID, detailed_message_to_admin, reply_markup=markup)

    if order.get("project_description_file_id"):
        file_id = order["project_description_file_id"]
        try:
            bot.send_document(CHANEL_CHAT_ID, file_id, caption="Методические указания к заказу.")
        except Exception as e:
            print(f"Ошибка при отправке файла: {e}")
            bot.send_message(CHANEL_CHAT_ID, "Ошибка при отправке файла методических указаний.")
    else:
        bot.send_message(CHANEL_CHAT_ID, "Файл методических указаний не прикреплен к заказу.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('complete_order_'))
def complete_order(call):
    order_id = int(call.data.split('_')[2])
    order = get_order_details(order_id)

    if order['is_partial_payment'] and not order['partial_payment_completed']:
        new_status = 2
        response_message = "Заказ ожидает завершения оплаты. Пожалуйста, завершите оплату, чтобы мы могли продолжить обработку."
        bot.send_message(call.message.chat.id, response_message)
    else:
        new_status = 3
        response_message = "Ваш заказ успешно завершён. Менеджер свяжется с вами в ближайшее время, чтобы отправить заказ!"
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"Заказ {order_id} выполнен и закрыт.")
        user_id = get_user_id_by_order_id(order_id)
        bot.send_message(user_id, response_message)

    update_order_status(order_id, order_status=new_status)
    bot.answer_callback_query(call.id, "Статус заказа обновлён.")


@app.route('/test', methods=['GET'])
def test_server():
    return jsonify({'status': 'success', 'message': 'Ура, победа'}), 200
