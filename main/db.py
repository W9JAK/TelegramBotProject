import psycopg2
from config import DATABASE_URL


# Возвращает соединение с базой данных.
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Извлекает параметры услуги по ее названию из базы данных.
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


# Обновляет информацию о пользователе в базе данных.
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


# Возвращает имя пользователя по его идентификатору из базы данных.
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


# Добавляет заказ в базу данных со всеми указанными параметрами.
def add_order(user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id=None, file_name=None, file_size=None):
    conn = psycopg2.connect(DATABASE_URL)
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id, file_name, file_size)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id, file_name, file_size))
            conn.commit()
    except Exception as e:
        print("Ошибка при добавлении заказа:", e)
    finally:
        conn.close()


# Удаляет заказ из базы данных по его идентификатору.
def delete_order(order_id):
    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
    conn.close()


# Возвращает список заказов конкретного пользователя.
def get_user_orders(user_id):
    conn = psycopg2.connect(DATABASE_URL)
    orders = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id, file_name, file_size
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
                'contents': row[13],
                'source_of_information': row[14],
                'promo_code': row[15],
                'project_description_file_id': row[16],
                'file_name': row[17],
                'file_size': row[18]
            } for row in cursor.fetchall()]
    except Exception as e:
        print("Ошибка при получении заказов пользователя:", e)
    finally:
        conn.close()
    return orders


def get_order_details(order_id):
    conn = get_db_connection()
    order_details = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, delivery_selected, project_title, project_description, project_requirements, speed_up, courier_delivery, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id, file_name, file_size
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
                    'promo_code': row[15],
                    'project_description_file_id': row[16],
                    'file_name': row[17],
                    'file_size': row[18]
                }
    except Exception as e:
        print(f"Ошибка при получении деталей заказа {order_id}:", e)
    finally:
        conn.close()
    return order_details
