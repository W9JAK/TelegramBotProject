from multiprocessing import Process
from main import start_bot
import logging

logger = logging.getLogger(__name__)


def run_telegram_bot():
    start_bot()


if __name__ == '__main__':
    logger.info("starting bot")
    print("starting bot")
    bot_process = Process(target=run_telegram_bot)

    bot_process.start()

    print("joining hinia")

    bot_process.join()

    print("bot started")
