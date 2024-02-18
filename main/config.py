import os
from os.path import join, dirname
from yookassa import Configuration
from dotenv import load_dotenv


def get_from_env(key):
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    return os.environ.get(key)


my_token = get_from_env("TELEGRAM_BOT_TOKEN")
Configuration.account_id = get_from_env("SHOP_ID")
Configuration.secret_key = get_from_env("PAYMENT_TOKEN")
DATABASE_URL = get_from_env("DATABASE_URL")
GROUP_CHAT_ID = get_from_env("GROUP_CHAT_ID")
