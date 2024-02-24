import time
import logging

import pandas as pd
import selenium
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from lxml import etree
from selenium.common import NoSuchElementException
from selenium.webdriver.common.by import By

from scraperai.utils.image import compress_b64_image
from scraperai.webdriver.manager import WebdriversManager
from scraperai.llm import OpenAIChatModel, OpenAIModel
from scraperai.parsing.pagination import PaginationDetector
from scraperai.parsing.catalog import CatalogParser
from scraperai.parsing.details import DetailsPageParser
from scraperai.parsing.classifier import GPTWebpageClassifier, WebpageType
from scraperai.utils import prettify_table
from scraperai.webdriver.remote import RemoteWebdriver
from scraperai.scraping.base import CatalogItem, BaseScraper

logger = logging.getLogger(__file__)


def fix_relative_url(base_url: str, url: str) -> str:
    if url.startswith('http'):
        return url
    return base_url + url.lstrip('/')


class ScraperAI(BaseScraper):
    def __init__(self,
                 api_key: str,
                 webmanager: WebdriversManager,
                 active_session_url: str = None,
                 active_session_id: str = None):

        self.api_key = api_key
        self.webmanager = webmanager
        self.current_url = None

        gpt4_model = OpenAIChatModel(self.api_key, OpenAIModel.gpt4)
        self.pagination_detector = PaginationDetector(gpt4_model)
        self.catalog_parser = CatalogParser(gpt4_model)
        self.details_parser = DetailsPageParser(gpt4_model)
        self.page_classifier = GPTWebpageClassifier(self.api_key)
        self.__pagination_screenshot: bytes | None = None

        if active_session_id:
            self.driver = self.webmanager.from_session_id(active_session_url, active_session_id)
        else:
            self.driver = self.webmanager.create_driver()

    def quit_driver(self):
        self.driver.quit()

    @property
    def pagination_screenshot(self) -> bytes | None:
        return self.__pagination_screenshot

    @property
    def total_spent(self) -> float:
        return self.pagination_detector.total_spent + \
            self.catalog_parser.total_spent + \
            self.page_classifier.total_spent + \
            self.details_parser.total_spent

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

        self.driver.set_window_size(1000, 2000)
        screenshot = compress_b64_image(self.driver.get_screenshot_as_base64(), aspect_ratio=0.5)
        return self.page_classifier.classify(screenshot)

    def detect_pagination(self, url: str) -> str | None:
        self.navigate(url)
        xpath = self.pagination_detector.find_xpath(self.driver.page_source)
        if xpath is None:
            return None

        try:
            element = self.driver.find_element(By.XPATH, xpath)
        except NoSuchElementException:
            return None

        self.__pagination_screenshot = element.screenshot_as_png
        element.screenshot("pagination.png")
        return xpath

    def detect_catalog_item(self, url: str) -> CatalogItem | None:
        """

        :param url:
        :return: {
            "card": "catalog card's classname",
            "url": "classname of element containing href url",
        }
        """
        self.navigate(url)
        classnames = self.catalog_parser.find_classnames(self.driver.page_source)
        if not classnames:
            return None
        # Highlight detected elements
        if classnames:
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
        ...

    def detect_details_on_page(self, url: str) -> dict[str, str]:
        ...

    def _switch_page(self, pagination_xpath) -> bool:
        try:
            elem = self.driver.find_element(By.XPATH, pagination_xpath)
            elem.click()
            time.sleep(3)
            return True
        except Exception as e:
            logger.exception(e)
            return False

    def collect_data_from_catalog_pages(self,
                                        start_url: str,
                                        pagination_xpath: str,
                                        card_classname: str,
                                        selectors: dict[str, str]) -> pd.DataFrame:
        def _map_card(card: BeautifulSoup) -> dict:
            data = {}
            dom = etree.HTML(str(card))
            for key, xpath in selectors.items():
                values = dom.xpath(xpath)
                data[key] = values[0].text if len(values) > 0 else None
            return data

        self.navigate(start_url)
        all_cards = []
        page_number = 0
        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            cards = soup.find_all(class_=card_classname)
            cards = [_map_card(card) for card in cards]

            all_cards += cards
            logger.info(f'Page: {page_number}: Found {len(cards)} new cards')

            success = self._switch_page(pagination_xpath)
            if not success:
                break

            page_number += 1
            if page_number >= 3:  # TODO: Remove this
                break

        logger.info(f'Totally found {len(all_cards)} cards')
        df = pd.DataFrame(all_cards)
        df = prettify_table(df)
        return df

    def collect_urls_to_nested_pages(self, start_url: str, pagination_xpath: str, url_classname: str) -> list[str]:
        self.navigate(start_url)

        components = urlparse(start_url)
        base_url = components.scheme + '://' + components.netloc + '/'

        urls = set()
        page_number = 0
        while True:
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            new_urls = [fix_relative_url(base_url, x['href']) for x in soup.find_all(class_=url_classname)]
            urls.update(new_urls)
            logger.info(f'Page: {page_number}: Found {len(new_urls)} new urls')
            try:
                elem = self.driver.find_element(By.XPATH, pagination_xpath)
                elem.click()
                time.sleep(3)
            except Exception as e:
                logger.exception(e)
                break

            page_number += 1
            if page_number >= 3:  # TODO: Remove this
                break

        logger.info(f'Totally found {len(urls)} urls')
        return list(urls)

    def collect_nested_pages(self, urls: list[str], selectors: dict[str, str]) -> pd.DataFrame:
        urls = urls[0:10]  # TODO: Remove this
        items = []
        for url in urls:
            self.navigate(url)
            time.sleep(1)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            dom = etree.HTML(str(soup))
            data = {}
            for key, xpath in selectors.items():
                values = dom.xpath(xpath)
                data[key] = values[0].text if len(values) > 0 else None
            items.append(data)
        df = pd.DataFrame(items)
        df['url'] = urls
        df = prettify_table(df)
        return df

    def parse_website(self, start_url: str) -> pd.DataFrame:
        logger.info(f'Start parsing "{start_url}"')

        # Get catalog page
        self.navigate(start_url)
        self.driver.get(start_url)

        # Find pagination
        pagination_xpath = self.detect_pagination(start_url)

        # Find urls selectors
        classnames = self.catalog_parser.find_classnames(self.driver.page_source)
        url_classname = classnames['url']
        logger.info(f'Found url classname: "{url_classname}"')

        urls = self.collect_urls_to_nested_pages(start_url, pagination_xpath, url_classname)

        self.navigate(urls[0])
        selectors = self.details_parser.to_selectors(self.driver.page_source)

        df = self.collect_nested_pages(urls, selectors)
        return df
