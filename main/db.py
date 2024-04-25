import psycopg2
from config import DATABASE_URL


# Возвращает соединение с базой данных.
def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn


# Извлекает параметры услуги по ее названию из базы данных.
def get_item_params_by_name_and_type(name, institution_type):
    conn = get_db_connection()
    item_params = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, amount, description, custom_description, speed_up_amount, speed_up_time, super_speed_up_amount, super_speed_up_time
                FROM items
                WHERE name = %s AND institution_type = %s
            """, (name, institution_type))
            row = cursor.fetchone()
            if row:
                item_params = {
                    'name': row[0],
                    'amount': row[1],
                    'description': row[2],
                    'custom_description': row[3],
                    'speed_up_amount': row[4],
                    'speed_up_time': row[5],
                    'super_speed_up_amount': row[6],
                    'super_speed_up_time': row[7]
                }
    except Exception as e:
        print(f"Ошибка при получении данных об услуге {name} для {institution_type}: {e}")
    finally:
        conn.close()
    return item_params


# Обновляет информацию о пользователе в базе данных.
def update_user_info(user_id, username, institution_type):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, username, institution_type)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE
                SET username = EXCLUDED.username, institution_type = EXCLUDED.institution_type;
            """, (user_id, username, institution_type))
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


def get_user_institution_type(user_id):
    conn = get_db_connection()
    institution_type = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT institution_type FROM users WHERE user_id = %s", (user_id,))
            result = cursor.fetchone()
            if result:
                institution_type = result[0]
    except Exception as e:
        print(f"Ошибка при получении типа учреждения пользователя {user_id}: {e}")
    finally:
        conn.close()
    return institution_type


def get_services_by_institution_type(institution_type):
    conn = get_db_connection()
    services = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT name, amount, description, custom_description
                FROM items
                WHERE institution_type = %s
            """, (institution_type,))
            services = [{'name': row[0], 'amount': row[1], 'description': row[2], 'custom_description': row[3]} for row in cursor.fetchall()]
    except Exception as e:
        print(f"Ошибка при получении услуг для {institution_type}: {e}")
    finally:
        conn.close()
    return services


# Добавляет заказ в базу данных со всеми указанными параметрами.
def add_order(user_id, item_id, amount, description, project_title, project_description, project_requirements, speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, contact_method, institution_type, subscription_discount_applied=False, project_description_file_id=None, file_name=None, file_size=None, payment_status=0, order_status=0):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO orders (user_id, item_id, amount, description, project_title, project_description, project_requirements, speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, contact_method, institution_type, subscription_discount_applied, project_description_file_id, file_name, file_size, payment_status, order_status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, item_id, amount, description, project_title, project_description, project_requirements, speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, contact_method, institution_type, subscription_discount_applied, project_description_file_id, file_name, file_size, payment_status, order_status))
            conn.commit()
    except Exception as e:
        print("Ошибка при добавлении заказа:", e)
    finally:
        conn.close()


# Удаляет заказ из базы данных по его идентификатору.
def delete_order(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при удалении заказа {order_id}: {e}")
    finally:
        conn.close()


def hide_order(order_id):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE orders SET is_visible = false WHERE order_id = %s", (order_id,))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении видимости заказа {order_id}: {e}")
    finally:
        conn.close()


# Записывает информацию о виде оплаты
def update_order_with_partial_payment_info(order_id, is_partial_payment):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            partial_payment_flag = 'TRUE' if is_partial_payment else 'FALSE'
            cursor.execute("""
                UPDATE orders
                SET is_partial_payment = %s
                WHERE order_id = %s
            """, (partial_payment_flag, order_id))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении информации о заказе {order_id}: {e}")
        conn.rollback()
    finally:
        conn.close()


def fetch_compilation_time(description, institution_type, speed_up):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT standard_completion_time, speed_up_time
                FROM items
                WHERE description = %s AND institution_type = %s
            """, (description, institution_type))
            result = cursor.fetchone()
            if result:
                return result[1] if speed_up else result[0]
    except Exception as e:
        print(f"Ошибка при получении времени на выполнение для {description}: {e}")
        return "н/д"
    finally:
        conn.close()


# Возвращает список заказов конкретного пользователя.
def get_user_orders(user_id):
    conn = get_db_connection()
    orders = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, project_title, project_description, project_requirements, speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, project_description_file_id, file_name, file_size, subscription_discount_applied, is_partial_payment, order_status
                FROM orders
                WHERE user_id = %s AND is_visible = true
            """, (user_id,))
            orders = [{
                'order_id': row[0],
                'user_id': row[1],
                'item_id': row[2],
                'amount': row[3],
                'description': row[4],
                'project_title': row[5],
                'project_description': row[6],
                'project_requirements': row[7],
                'speed_up': row[8],
                'education_institution_name': row[9],
                'has_contents': row[10],
                'contents': row[11],
                'source_of_information': row[12],
                'promo_code': row[13],
                'project_description_file_id': row[14],
                'file_name': row[15],
                'file_size': row[16],
                'subscription_discount_applied': row[17],
                'is_partial_payment': row[18],
                'order_status': row[19]
            } for row in cursor.fetchall()]
    except Exception as e:
        print("Ошибка при получении заказов пользователя:", e)
    finally:
        conn.close()
    return orders


# Извлекает и возвращает детали заказа по его идентификатору из базы данных
def get_order_details(order_id):
    conn = get_db_connection()
    order_details = {}
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT order_id, user_id, item_id, amount, description, project_title, project_description, project_requirements, speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, contact_method, institution_type, project_description_file_id, file_name, file_size, subscription_discount_applied, is_partial_payment, partial_payment_completed
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
                    'project_title': row[5],
                    'project_description': row[6],
                    'project_requirements': row[7],
                    'speed_up': row[8],
                    'education_institution_name': row[9],
                    'has_contents': row[10],
                    'contents': row[11],
                    'source_of_information': row[12],
                    'promo_code': row[13],
                    'contact_method': row[14],
                    'institution_type': row[15],
                    'project_description_file_id': row[16],
                    'file_name': row[17],
                    'file_size': row[18],
                    'subscription_discount_applied': row[19],
                    'is_partial_payment': row[20],
                    'partial_payment_completed': row[21]
                }
    except Exception as e:
        print(f"Ошибка при получении деталей заказа {order_id}:", e)
    finally:
        conn.close()
    return order_details


def update_order_status(order_id, payment_status=None, order_status=None, is_partial_payment=None, partial_payment_completed=None):
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            if payment_status is not None:
                cursor.execute("UPDATE orders SET payment_status = %s WHERE order_id = %s", (payment_status, order_id))
            if order_status is not None:
                cursor.execute("UPDATE orders SET order_status = %s WHERE order_id = %s", (order_status, order_id))
            if is_partial_payment is not None:
                cursor.execute("UPDATE orders SET is_partial_payment = %s WHERE order_id = %s", (is_partial_payment, order_id))
            if partial_payment_completed is not None:
                cursor.execute("UPDATE orders SET partial_payment_completed = %s WHERE order_id = %s", (partial_payment_completed, order_id))
            conn.commit()
    except Exception as e:
        print(f"Ошибка при обновлении статуса заказа {order_id}: {e}")
    finally:
        conn.close()


def get_user_id_by_order_id(order_id):
    conn = get_db_connection()
    user_id = None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT user_id FROM orders WHERE order_id = %s", (order_id,))
            result = cursor.fetchone()
            if result:
                user_id = result[0]
    except Exception as e:
        print(f"Ошибка при получении user_id для заказа {order_id}: {e}")
    finally:
        conn.close()
    return user_id
