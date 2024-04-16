import logging
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as BaseSeleniumWebDriver

from scraperai.crawlers.base import BaseCrawler
from scraperai.crawlers.webdriver import utils
from scraperai.crawlers.webdriver.local import DefaultChromeWebdriver
from scraperai.models import Pagination
from scraperai.utils import add_or_replace_url_param, get_url_query_param_value

logger = logging.getLogger('scraperai')


class SeleniumCrawler(BaseCrawler):

    def __init__(self, driver: BaseSeleniumWebDriver = None):
        if driver is None:
            self.driver = DefaultChromeWebdriver()
        else:
            self.driver = driver
        self.__last_height = None

    def get(self, url: str):
        if self.driver.current_url == url:
            return
        self.driver.get(url)
        time.sleep(1)

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    def click(self, xpath: str) -> None:
        elem = self.driver.find_element(By.XPATH, xpath)
        elem.click()

    def get_screenshot_as_base64(self) -> str:
        self.driver.execute_script("document.body.style.zoom='60%'")
        screenshot = self.driver.get_screenshot_as_base64()
        self.driver.execute_script("document.body.style.zoom='100%'")
        return screenshot

    def highlight_by_xpath(self, xpath: str, color: str, border: int):
        utils.highlight_by_xpath(self.driver, xpath, color, border)

    def _scroll(self, times: int = 10, delay: float = 0.4):
        for _ in range(times):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(delay)

    def scroll_to_bottom(self) -> bool:
        """Scrolls the webpage to the bottom using Selenium"""
        curr_height = self.driver.execute_script("return document.body.scrollHeight")
        self._scroll()
        if self.__last_height == curr_height:
            time.sleep(5)
            self._scroll()
        time.sleep(2)
        if self.__last_height == curr_height:
            self.__last_height = None
            return False
        else:
            self.__last_height = self.driver.execute_script("return document.body.scrollHeight")
            return True

    def switch_page(self, pagination: Pagination) -> bool:
        # TODO: Need a way to understand when to stop changing pages
        if pagination.type == 'xpath':
            try:
                self.click(pagination.xpath)
                time.sleep(3)
                return True
            except selenium.common.exceptions.ElementClickInterceptedException as e:
                logger.exception(e)
                return False
            except Exception as e:
                logger.exception(e)
                return False
        elif pagination.type == 'url_param':
            params = get_url_query_param_value(self.driver.current_url, pagination.url_param)
            if params is None:
                new_page = pagination.url_param_first_value
            else:
                new_page = int(params[0]) + 1
            new_url = add_or_replace_url_param(self.driver.current_url, pagination.url_param, new_page)
            self.get(new_url)
            # TODO: How to stop pagination?
            return True
        elif pagination.type == 'scroll':
            return self.scroll_to_bottom()
        else:
            raise TypeError
