import time
from threading import Thread
import main
from telebot import TeleBot


bot = TeleBot(main.my_token)


def run_bot():
    while True:
        try:
            print("Запуск бота...")
            bot.polling(none_stop=True)
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
