import pandas as pd
import subprocess
from db import get_db_connection


# Функция для извлечения данных из базы данных
def fetch_data():
    query = """
    SELECT order_id, user_id, item_id, amount, project_title, project_description, project_requirements, 
           speed_up, education_institution_name, has_contents, contents, source_of_information, promo_code, 
           subscription_discount_applied, is_partial_payment, order_status 
    FROM orders 
    WHERE order_status != 0
    """
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


# Функция для сохранения DataFrame в файл Excel
def save_to_excel(df):
    with pd.ExcelWriter("orders.xlsx", engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    with open("orders.xlsx", "rb") as f:
        excel_data = f.read()
    return excel_data


def sync_to_yandex_disk(file_path, remote_path):
    command = ["copy", file_path, f"YandexDisk:{remote_path}"]
    subprocess.run(command, check=True)


# Главная функция для запуска всех операций
def main():
    print("Загрузка данных...")
    df = fetch_data()
    print("Сохранение данных в Excel...")
    save_to_excel(df)
    print("Синхронизация файла с Яндекс.Диском...")
    sync_to_yandex_disk("orders.xlsx", "Freebies")
    print("Операция завершена.")


if __name__ == "__main__":
    main()
