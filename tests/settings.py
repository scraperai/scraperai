import logging
import os
from pathlib import Path
from dotenv import load_dotenv

from scraperai.crawlers.webdriver import SelenoidSettings, WebdriversManager

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filemode='a',
    encoding='utf-8',
    level=logging.INFO
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / 'tests' / 'data'
if os.path.exists(BASE_DIR / '.env'):
    load_dotenv(BASE_DIR / '.env')

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
SELENOID_URL = os.getenv('SELENOID_URL')

selenoid_capabilities = {
    "browserName": "firefox",
    "browserVersion": "115.0",
    "selenoid:options": {
        "name": "scraperai",
        "enableVideo": False,
        "enableVNC": True,
        # "screenResolution": "1280x1024x24",
        "sessionTimeout": '5m'
    },
}
default_webmanager = WebdriversManager(selenoids=[
    SelenoidSettings(url=SELENOID_URL, max_sessions=50, capabilities=selenoid_capabilities)
])
