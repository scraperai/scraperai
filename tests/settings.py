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

BASE_DIR = Path(__file__).resolve().parent.parent
if os.path.exists(BASE_DIR / '.env'):
    load_dotenv(BASE_DIR / '.env')

OPEN_AI_TOKEN = os.getenv('OPEN_AI_TOKEN')
SELENOID_URL = os.getenv('SELENOID_URL')

selenoid_capabilities = {
    "browserName": "chrome",
    "browserVersion": "119.0",
    "selenoid:options": {
        "enableVideo": False
    },
    "sessionTimeout": '2h'
}
