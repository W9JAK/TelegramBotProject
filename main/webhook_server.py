from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from main import bot, get_db_connection, get_user_username
from config import GROUP_CHAT_ID


app = Flask(__name__)


# Извлекает и возвращает детали заказа по его идентификатору из базы данных
def get_order_details(order_id):
    conn = get_db_connection()
    order_details = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code 
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
                    'contents': row[13],
                    'source_of_information': row[14],
                    'promo_code': row[15]
                }
    except Exception as e:
        print(f"Ошибка при получении деталей заказа {order_id}:", e)
    finally:
        conn.close()
    return order_details


# Обрабатывает вебхук от YooKassa для подтверждения оплаты заказа
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

        if order.get("promo_code"):
            message += f'Промокод: {order["promo_code"]}\n'
        else:
            message += f'Откуда узнали: {order.get("source_of_information", "Не указано")}\n'

        if user_username:
            message += f'Заказчик: @{user_username}\n'
        else:
            message += 'Информация о заказчике недоступна.\n'

        with open("orders_log.txt", "a") as file:
            file.write(f"{message}\r\n")

        bot.send_message(GROUP_CHAT_ID, message)

    return jsonify({'status': 'success'})


@app.route('/orders')
def show_orders():
    try:
        with open("orders_log.txt", "r", encoding="windows-1251") as file:
            orders_data = file.read()
    except FileNotFoundError:
        orders_data = "Файл с данными о заказах не найден."

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Заказы</title>
    </head>
    <body>
        <h1>Заказы</h1>
        <pre>{{ orders_data }}</pre>
    </body>
    </html>
    """
    return render_template_string(html_template, orders_data=orders_data)


if __name__ == '__main__':
    app.run(debug=True)
