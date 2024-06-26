import logging
import time

import selenium
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as BaseSeleniumWebDriver

from scraperai.crawlers.base import BaseCrawler
from scraperai.crawlers.webdriver import utils
from scraperai.crawlers.webdriver.local import DefaultChromeWebdriver
from scraperai.models import Pagination

logger = logging.getLogger('scraperai')


class SeleniumCrawler(BaseCrawler):

    def __init__(self, driver: BaseSeleniumWebDriver = None):
        if driver is None:
            self.driver = DefaultChromeWebdriver()
        else:
            self.driver = driver
        self.__last_height = None
        self.__pagination_url_index = 0

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

    def get_screenshot_as_base64(self, zoom_out: bool = True) -> str:
        if zoom_out:
            self.driver.execute_script("document.body.style.zoom='60%'")
        screenshot = self.driver.get_screenshot_as_base64()
        if zoom_out:
            self.driver.execute_script("document.body.style.zoom='100%'")
        return screenshot

    def highlight_by_xpath(self, xpath: str, color: str, border: int):
        utils.highlight_by_xpath(self.driver, xpath, color, border)

    def back(self):
        self.driver.back()

    def _scroll(self) -> bool:
        prev_y = self.driver.execute_script('return window.pageYOffset;')
        self.driver.execute_script("window.scrollBy(0, 500);")
        curr_y = self.driver.execute_script('return window.pageYOffset;')
        return prev_y != curr_y

    def switch_page(self, pagination: Pagination) -> bool:
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
        elif pagination.type == 'urls':
            if self.__pagination_url_index >= len(pagination.urls):
                return False
            self.get(pagination.urls[self.__pagination_url_index])
            self.__pagination_url_index += 1
            return True
        elif pagination.type == 'scroll':
            return self._scroll()
        else:
            return False
