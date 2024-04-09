from flask import Flask, request, jsonify
from datetime import datetime
from main import bot
from config import CHANEL_CHAT_ID
from db import get_order_details, get_user_username


app = Flask(__name__)


# Обрабатывает вебхук от YooKassa для подтверждения оплаты заказа
@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    data = request.json
    print("Received webhook data:", data)
    if data.get('event') == 'payment.succeeded':
        order_id = data['object']['metadata'].get('order_id')
        if not order_id:
            print("order_id отсутствует в метаданных платежа")
            return jsonify({'status': 'error', 'message': 'order_id is missing'}), 400

        order = get_order_details(order_id)
        if not order:
            print(f"Информация о заказе с ID {order_id} не найдена.")
            return jsonify({'status': 'error', 'message': 'order details not found'}), 404

        user_id = order['user_id']
        user_username = get_user_username(user_id)
        payment_time = datetime.now().strftime('%H:%M:%S %Y-%m-%d')
        content_line = f'Содержание: {order["contents"]}\n' if order.get("contents") else ""
        payment_type = "Частичная оплата" if order.get("is_partial_payment") else "Полная оплата"

        message_to_admin = (
            f'{order["description"]} за {order["amount"]} рублей\n'
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
            message_to_admin += f'Промокод: {order["promo_code"]}\n'
        else:
            message_to_admin += f'Откуда узнали: {order.get("source_of_information", "Не указано")}\n'

        if user_username:
            message_to_admin += f'Заказчик: @{user_username}\n'
        else:
            message_to_admin += f'Информация о аккаунте тг заказчика недоступна.\n'

        bot.send_message(CHANEL_CHAT_ID, message_to_admin)

        if order.get("project_description_file_id"):
            file_id = order["project_description_file_id"]
            try:
                bot.send_document(CHANEL_CHAT_ID, file_id, caption="Методические указания к заказу.")
            except Exception as e:
                print(f"Ошибка при отправке файла: {e}")
                bot.send_message(CHANEL_CHAT_ID, "Ошибка при отправке файла методических указаний.")
        else:
            bot.send_message(CHANEL_CHAT_ID, "Файл методических указаний не прикреплен к заказу.")

        user_message = "Ваш заказ был успешно оплачен и взят в работу. Мы сообщим вам о ходе выполнения. Спасибо за доверие!"

        try:
            bot.send_message(user_id, user_message)
        except Exception as e:
            print(f"Ошибка при отправке сообщения пользователю: {e}")

    return jsonify({'status': 'success'})
