import random
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from scraperai.browser.base import BrowserScraper
from scraperai.browser.storage import LocalStorage

# Initializing a list with two Useragents
with open(Path(__file__).resolve().parent / 'useragents.txt', 'r') as f:
    useragentarray = list(f.read().split('\n'))


class LocalBrowserScraper(BrowserScraper):
    @staticmethod
    def _setup_options() -> Options:
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("--window-size=1440, 900")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36')

        # Anti bot
        # Adding argument to disable the AutomationControlled flag
        options.add_argument("--disable-blink-features=AutomationControlled")
        # Exclude the collection of enable-automation switches
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # Turn-off userAutomationExtension
        options.add_experimental_option("useAutomationExtension", False)

        return options

    def __init__(self):
        self.options = self._setup_options()
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=self.options)
        self.local_storage = LocalStorage(self.driver)

        # Changing the property of the navigator value for webdriver to undefined
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def get(self, url: str):
        index = random.randint(0, len(useragentarray) - 1)
        self.driver.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": useragentarray[index]})
        self.driver.get(url)

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    def wait(self, timeout: float, locator):
        WebDriverWait(self.driver, timeout).until(locator)

    def set_storage(self, key, value):
        self.local_storage.set(key, value)

    def execute_cdp_cmd(self, cmd: str, cmd_args: dict):
        self.driver.execute_cdp_cmd(cmd, cmd_args)

    def close(self):
        self.driver.close()
