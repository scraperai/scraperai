import typing as tp

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from .utils import highlight
from .base import BaseWebdriver
from .storage import LocalStorage
from .useragents import get_random_useragent


class LocalWebdriver(webdriver.Chrome, BaseWebdriver):
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

    def __init__(self, on_quit: tp.Callable[[], None] = None):
        self.on_quit = on_quit
        self.url = 'local'
        self.options = self._setup_options()
        super().__init__(service=Service(ChromeDriverManager().install()), options=self.options)
        self.local_storage = LocalStorage(self)

        # Changing the property of the navigator value for webdriver to undefined
        self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    def get_session_id(self) -> str:
        return self.session_id

    def get(self, url: str):
        self.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": get_random_useragent()})
        super().get(url)

    def wait(self, timeout: float, locator):
        WebDriverWait(self, timeout).until(locator)

    def set_storage(self, key, value):
        self.local_storage.set(key, value)

    def quit(self) -> None:
        if self.on_quit:
            self.on_quit()
        super().quit()

    def highlight(self, element: WebElement, color: str, border: int):
        highlight(self, element, color, border)
