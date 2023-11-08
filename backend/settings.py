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

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')

DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL")


TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": [
                "admin.models",
                "api.auth.models",
                "api.users.models",
                "api.subscriptions.models",
                "aerich.models"
            ],
            "default_connection": "default",
        }
    },
}
