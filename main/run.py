from multiprocessing import Process
from main import start_bot


def run_telegram_bot():
    start_bot()


if __name__ == '__main__':
    bot_process = Process(target=run_telegram_bot)

    bot_process.start()

    bot_process.join()
