import time
from threading import Thread
from main import start_bot


def run_bot():
    while True:
        try:
            print("Запуск бота...")
            start_bot()
        except Exception as e:
            print(f"Произошла ошибка: {e}")
            time.sleep(10)


# Функция для запуска веб-сервера с использованием waitress
def run_waitress_server():
    from serve import serve, app
    print("Запуск веб-сервера...")
    serve(app, host='0.0.0.0', port=8080)


if __name__ == "__main__":
    bot_thread = Thread(target=run_bot)
    bot_thread.start()

    run_waitress_server()
