import logging
import threading
import time
import typing as tp

from dataclasses import dataclass

from .base import BaseWebdriver
from .local import LocalWebdriver
from .remote import RemoteWebdriver


logger = logging.getLogger(__file__)


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

    def start_driver(self) -> BaseWebdriver:
        """
        Implementation for starting a selenium driver for multiple endpoints.

        It uses multithreading and applies a lock to make the number of connections threadsafe.

        TBD if this needs to be async.
        """
        while True:
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

            logging.info("All URLs have reached the maximum number of connections. Waiting...")
            time.sleep(3)

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
