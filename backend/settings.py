import datetime
import logging
import os
from pathlib import Path
from dotenv import load_dotenv


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a',
    encoding='utf-8',
    level=logging.INFO
)

BASE_DIR = Path(__file__).resolve().parent
if os.path.exists(BASE_DIR / '.env'):
    load_dotenv(BASE_DIR / '.env')

SECRET_KEY = os.getenv('SECRET_KEY')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
YANDEX_CLIENT_ID = os.getenv('YANDEX_CLIENT_ID')
YANDEX_CLIENT_SECRET = os.getenv('YANDEX_CLIENT_SECRET')

SMTP_HOST = os.getenv('SMTP_HOST')
SMTP_PORT = os.getenv('SMTP_PORT')
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

TINKOFF_API_URL = 'https://securepay.tinkoff.ru/v2'
TINKOFF_TERMINAL_KEY = os.getenv('TINKOFF_TERMINAL_KEY')
TINKOFF_PASSWORD = os.getenv('TINKOFF_PASSWORD')
TINKOFF_PAYMENT_SESSION_LIFETIME = datetime.timedelta(minutes=20)

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")


TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "models.auth.models",
                "models.users.models",
                "models.payments.models",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    },
}
