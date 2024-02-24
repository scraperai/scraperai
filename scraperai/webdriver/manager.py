import logging
import typing as tp

from dataclasses import dataclass

from urllib.parse import urlparse
import requests

from .base import BaseWebdriver
from .local import LocalWebdriver
from .remote import RemoteWebdriver


logger = logging.getLogger(__file__)


class TooManySessions(Exception):
    """Too many sessions """


@dataclass
class SelenoidSettings:
    url: str
    max_sessions: int
    capabilities: dict[str, tp.Any] = None
    timeout: float = 60


class WebdriversManager:
    def __init__(self, selenoids: list[SelenoidSettings] = None):
        self.selenoids = selenoids
        self.local_sessions = 0

    @staticmethod
    def _get_active_sessions(selenoid: SelenoidSettings) -> int:
        params = urlparse(selenoid.url)
        url = params.scheme + '://' + params.netloc + '/status'
        response = requests.get(url).json()
        return response['used']

    def from_session_id(self, url: str, session_id: str) -> BaseWebdriver:
        if url == 'local':
            raise ValueError
        for selenoid in self.selenoids:
            if selenoid.url == url:
                driver = RemoteWebdriver.from_session_id(url=selenoid.url,
                                                         capabilities=selenoid.capabilities,
                                                         session_id=session_id)
                return driver
        raise KeyError(f'Session not found for url="{url}" session_id="{session_id}"')

    def _on_local_quit(self):
        self.local_sessions -= 1

    def create_driver(self) -> LocalWebdriver | RemoteWebdriver:
        """
        Implementation for starting a selenium driver for multiple endpoints.
        """
        for selenoid in self.selenoids:
            if selenoid.url == 'local':
                active_sessions = self.local_sessions
            else:
                active_sessions = self._get_active_sessions(selenoid)
            if active_sessions < selenoid.max_sessions:
                logger.debug(f"Starting the webdriver for {selenoid.url} with "
                             f"current {active_sessions} sessions")
                if selenoid.url == 'local':
                    driver = LocalWebdriver(on_quit=self._on_local_quit)
                    self.local_sessions += 1
                else:
                    driver = RemoteWebdriver(url=selenoid.url, capabilities=selenoid.capabilities)
                driver.set_page_load_timeout(selenoid.timeout)
                driver.implicitly_wait(selenoid.timeout)
                return driver

        raise TooManySessions()
