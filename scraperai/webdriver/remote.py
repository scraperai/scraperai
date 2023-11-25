import typing as tp

import json

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait

from .base import BaseWebdriver
from .storage import LocalStorage
from .useragents import get_random_useragent


class RemoteWebdriver(webdriver.Remote, BaseWebdriver):
    def __init__(self, url: str, capabilities: dict[str, tp.Any]):
        super().__init__(command_executor=url, desired_capabilities=capabilities)
        self.url = url
        self.local_storage = LocalStorage(self)

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
