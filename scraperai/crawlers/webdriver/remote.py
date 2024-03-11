from __future__ import annotations

import copy
import typing as tp

import json
from urllib.parse import urlparse

from selenium import webdriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions

from .base import BaseWebdriver
from .utils import highlight
from .storage import LocalStorage
from .useragents import get_random_useragent


def _make_firefox_options() -> FirefoxOptions:
    opts = FirefoxOptions()
    opts.set_preference("general.useragent.override",
                        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
    return opts


def _make_chrome_options() -> ChromeOptions:
    options = ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36")
    options.add_argument("--ignore-certificate-errors")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Anti bot
    # Adding argument to disable the AutomationControlled flag
    options.add_argument("--disable-blink-features=AutomationControlled")
    # Exclude the collection of enable-automation switches
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # Turn-off userAutomationExtension
    options.add_experimental_option("useAutomationExtension", False)

    return options


class RemoteWebdriver(webdriver.Remote, BaseWebdriver):
    def __init__(self, url: str, capabilities: dict[str, tp.Any]):
        if capabilities['browserName'] == 'chrome':
            capabilities.update(_make_chrome_options().to_capabilities())
        elif capabilities['browserName'] == 'firefox':
            capabilities.update(_make_firefox_options().to_capabilities())
        else:
            raise Exception('Invalid browser name')

        super().__init__(command_executor=url, desired_capabilities=capabilities)
        self.url = url
        self.local_storage = LocalStorage(self)

        # Changing the property of the navigator value for webdriver to undefined
        self.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    @staticmethod
    def from_session_id(url: str, capabilities: dict[str, tp.Any], session_id: str) -> RemoteWebdriver:
        driver = RemoteWebdriver(url, capabilities)
        driver_copy = copy.copy(driver)
        driver.quit()
        driver_copy.session_id = session_id
        return driver_copy

    def get_session_id(self) -> str:
        return self.session_id

    def get(self, url: str):
        self.execute_cdp_cmd("Network.setUserAgentOverride", {"userAgent": get_random_useragent()})
        super().get(url)

    def wait(self, timeout: float, locator):
        WebDriverWait(self, timeout).until(locator)

    def set_storage(self, key, value):
        self.local_storage.set(key, value)

    def execute_cdp_cmd(self, cmd: str, cmd_args: dict):
        resource = "/session/%s/chromium/send_command_and_get_result" % self.session_id
        url = self.command_executor._url + resource
        body = json.dumps({'cmd': cmd, 'params': cmd_args})
        response = self.command_executor._request('POST', url, body)
        return response.get('value')

    def highlight(self, element: WebElement, color: str, border: int):
        highlight(self, element, color, border)

    @property
    def vnc_url(self) -> str:
        return f'ws://{urlparse(self.url).netloc}/vnc/{self.session_id}'
