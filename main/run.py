from multiprocessing import Process
import webhook_server
from main import start_bot


def run_flask_app():
    from waitress import serve
    serve(webhook_server.app, host='0.0.0.0', port=8080)


def run_telegram_bot():
    start_bot()


if __name__ == '__main__':
    flask_process = Process(target=run_flask_app)
    bot_process = Process(target=run_telegram_bot)

    flask_process.start()
    bot_process.start()

    flask_process.join()
    bot_process.join()
