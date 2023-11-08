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
OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
DATABASE_URL = os.getenv("DATABASE_URL")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")


TORTOISE_ORM = {
    "connections": {"default": DATABASE_URL},
    "apps": {
        "models": {
            "models": ["admin.models", "api.auth.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
