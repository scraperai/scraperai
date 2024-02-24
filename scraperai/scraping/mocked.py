import time
from pathlib import Path
from urllib.parse import urlparse

import pandas as pd
import selenium
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from scraperai.webdriver.manager import WebdriversManager
from scraperai.parsing.classifier import WebpageType
from scraperai.scraping.base import BaseScraper, CatalogItem
from scraperai.webdriver.remote import RemoteWebdriver


class MockedScraper(BaseScraper):
    def __init__(self,
                 webmanager: WebdriversManager,
                 active_session_url: str = None,
                 active_session_id: str = None):

        self.__mockurl = 'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods-company/view/30'
        self.webmanager = webmanager
        self.current_url = None

        self.__pagination_screenshot: bytes | None = None

        if active_session_id:
            self.driver = self.webmanager.from_session_id(active_session_url, active_session_id)
        else:
            self.driver = self.webmanager.create_driver()

    @property
    def pagination_screenshot(self) -> bytes | None:
        return self.__pagination_screenshot

    @property
    def total_spent(self) -> float:
        return 200.0

    @property
    def session_id(self) -> str:
        return self.driver.session_id

    @property
    def session_url(self) -> str:
        return self.driver.url

    @property
    def vnc_url(self) -> str | None:
        if isinstance(self.driver, RemoteWebdriver):
            return f'ws://{urlparse(self.driver.url).netloc}/vnc/{self.session_id}'
        return None

    def navigate(self, url: str):
        url = self.__mockurl
        if self.current_url == url:
            return

        try:
            self.driver.get(url)
        except selenium.common.exceptions.InvalidSessionIdException:
            self.driver = self.webmanager.create_driver()
            self.driver.get(url)
        except Exception as e:
            self.driver.quit()
            raise e

        time.sleep(1)
        self.current_url = url

    def detect_page_type(self, url: str) -> WebpageType:
        self.navigate(url)
        return WebpageType.CATALOG

    def detect_pagination(self, url: str) -> str | None:
        self.navigate(url)
        xpath = '/html/body/div/main/section[3]/div/div[2]/button'
        try:
            element = self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

        self.__pagination_screenshot = element.screenshot_as_png
        return xpath

    def detect_catalog_item(self, url: str) -> CatalogItem | None:
        self.navigate(url)

        classnames = {
            'card': 'product',
            'url': 'product_img'
        }
        element = self.driver.find_element(By.CLASS_NAME, classnames['card'])
        self.driver.execute_script("arguments[0].scrollIntoView();", element)

        for classname in classnames.values():
            for element in self.driver.find_elements(By.CLASS_NAME, classname):
                self.driver.highlight(element, 'red', 5)
        return CatalogItem(
            card_classname=classnames['card'],
            url_classname=classnames['url'],
            html_snippet='',
            url=''
        )

    def detect_details_on_card(self, html_snippet: str) -> dict[str, str]:
        return {
            'Название': '/div/h4',
            'Цена': '/div/div[1]',
            'Изображение': '/a/img',
        }

    def detect_details_on_page(self, url: str) -> dict[str, str]:
        url = 'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/293563'
        self.navigate(url)
        return {
            'Название': '/html/body/div/main/div/div/div[2]/div/div[1]/div[1]/h1',
            'Артикул': '/html/body/div/main/div/div/div[2]/div/div[1]/div[4]/p',
            'Описание': '/html/body/div/main/div/div/div[2]/div/div[2]',
            'Цена': '/html/body/div/main/div/div/div[2]/div/div[3]/div/div/span',
            'Изображение': '//*[@id="curr-image-block"]/img',
        }

    def collect_data_from_catalog_pages(self,
                                        start_url: str,
                                        pagination_xpath: str,
                                        card_classname: str,
                                        selectors: dict[str, str]) -> pd.DataFrame:
        self.navigate(start_url)
        base_dir = Path(__file__).resolve().parent
        return pd.read_excel(base_dir / 'mockdata.xlsx', header=0)

    def collect_urls_to_nested_pages(self, start_url: str, pagination_xpath: str, url_classname: str) -> list[str]:
        self.navigate(start_url)
        return [
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/281600',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/282880',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/286153',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/281344',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/281856',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/281438',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/285982',
            'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/281208'
        ]

    def collect_nested_pages(self, urls: list[str], selectors: dict[str, str]) -> pd.DataFrame:
        base_dir = Path(__file__).resolve().parent
        return pd.read_excel(base_dir / 'mockdata.xlsx', header=0)
