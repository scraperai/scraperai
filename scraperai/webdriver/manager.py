import logging
import threading
import typing as tp

from dataclasses import dataclass

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
    timeout: float = 10


class WebdriversManager:
    def __init__(self, selenoids: list[SelenoidSettings] = None):
        self.selenoids = selenoids
        self.connections = {selenoid.url: 0 for selenoid in selenoids}
        self.lock = threading.Lock()

    def from_session_id(self, url: str, session_id: str) -> BaseWebdriver:
        if url == 'local':
            raise ValueError
        with self.lock:
            for selenoid in self.selenoids:
                if selenoid.url == url:
                    driver = RemoteWebdriver.from_session_id(url=selenoid.url,
                                                             capabilities=selenoid.capabilities,
                                                             session_id=session_id)
                    return driver
        raise KeyError('Session not found')

    def start_driver(self) -> BaseWebdriver:
        """
        Implementation for starting a selenium driver for multiple endpoints.
        """
        with self.lock:
            for selenoid in self.selenoids:
                if self.connections[selenoid.url] < selenoid.max_sessions:
                    logger.debug(f"Starting the webdriver for {selenoid.url} with "
                                 f"current {self.connections[selenoid.url]} sessions")
                    if selenoid.url == 'local':
                        driver = LocalWebdriver()
                    else:
                        driver = RemoteWebdriver(url=selenoid.url, capabilities=selenoid.capabilities)
                    driver.set_page_load_timeout(selenoid.timeout)
                    driver.implicitly_wait(selenoid.timeout)
                    self.connections[selenoid.url] += 1
                    return driver

        raise TooManySessions()

    def quit_driver(self, driver: BaseWebdriver) -> None:
        try:
            url = driver.url
            with self.lock:
                self.connections[url] -= 1
                logging.info(f"Removing session from {url}, {self.connections[url]} sessions now.")
            driver.quit()
        except Exception as e:
            logger.exception(e)
        return None
