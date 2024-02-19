from flask import Flask, request, jsonify
from datetime import datetime
from main import bot, get_db_connection, get_user_username
from config import GROUP_CHAT_ID

app = Flask(__name__)


def get_order_details(order_id):
    conn = get_db_connection()
    order_details = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents
                FROM orders
                WHERE order_id = %s
            """, (order_id,))
            row = cursor.fetchone()
            if row:
                order_details = {
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
                }
    except Exception as e:
        print(f"Ошибка при получении деталей заказа {order_id}:", e)
    finally:
        conn.close()
    return order_details


@app.route('/webhook/yookassa', methods=['POST'])
def yookassa_webhook():
    data = request.json
    if data.get('event') == 'payment.succeeded':
        order_id = data['object']['metadata'].get('order_id')
        if not order_id:
            print("order_id отсутствует в метаданных платежа")
            return jsonify({'status': 'error', 'message': 'order_id is missing'}), 400

        order = get_order_details(order_id)
        if not order:
            print(f"Информация о заказе с ID {order_id} не найдена.")
            return jsonify({'status': 'error', 'message': 'order details not found'}), 404

        user_username = get_user_username(order['user_id'])  # Получаем username пользователя
        payment_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Примерное время оплаты

        message = (
            f'{order["description"]} за {order["amount"]} рублей\n'
            f'Название учебного заведения: {order["education_institution_name"]}\n'
            f'Тема работы: {order["project_title"]}\n'
            f'Методические указания: {order["project_description"]}\n'
            f'Содержание: {order.get("contents", "Не указано")}\n'
            f'Пожелания к работе: {order["project_requirements"]}\n'
            f'Ускоренное выполнение: {"Да" if order["speed_up"] else "Нет"}\n'
            f'Курьерская доставка: {"Да" if order["courier_delivery"] else "Нет"}\n'
            f'Время оплаты: {payment_time}\n'
            f'ID заказчика: {order["user_id"]}\n'
        )

        # Если username доступен, добавляем его в сообщение
        if user_username:
            message += f'Заказчик: @{user_username}\n'
        else:
            message += 'Информация о заказчике недоступна.\n'

        bot.send_message(GROUP_CHAT_ID, message)

    return jsonify({'status': 'success'})


if __name__ == '__main__':
    app.run(debug=True)
