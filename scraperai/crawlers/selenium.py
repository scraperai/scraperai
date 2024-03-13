import time

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver as BaseSeleniumWebDriver

from scraperai.crawlers.base import BaseCrawler
from scraperai.crawlers.webdriver.local import DefaultChromeWebdriver


class SeleniumCrawler(BaseCrawler):
    def __init__(self, driver: BaseSeleniumWebDriver = None):
        if driver is None:
            self.driver = DefaultChromeWebdriver()
        else:
            self.driver = driver
        self.current_url = None

    def get(self, url: str):
        if self.current_url == url:
            return
        self.driver.get(url)
        time.sleep(1)
        self.driver.execute_script("document.body.style.zoom='60%'")
        self.current_url = url

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    def click(self, xpath: str) -> None:
        elem = self.driver.find_element(By.XPATH, xpath)
        elem.click()

    def get_screenshot_as_base64(self) -> str:
        return self.driver.get_screenshot_as_base64()
