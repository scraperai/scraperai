import requests

from scraperai.crawlers.base import BaseCrawler
from scraperai.models import Pagination


class RequestsCrawler(BaseCrawler):
    current_url: str = None

    def __init__(self):
        self.__page_source = None
        self.__pagination_url_index = 0

    def get(self, url: str):
        self.current_url = url
        self.__page_source = requests.get(url).text

    @property
    def page_source(self) -> str:
        return self.__page_source

    def click(self, xpath: str) -> None:
        raise NotImplementedError()

    def get_screenshot_as_base64(self) -> str:
        raise NotImplementedError()

    def switch_page(self, pagination: Pagination) -> bool:
        if pagination.type == 'urls':
            if self.__pagination_url_index >= len(pagination.urls):
                return False
            self.get(pagination.urls[self.__pagination_url_index])
            self.__pagination_url_index += 1
            return True
        elif pagination.type == 'xpath':
            return False
        elif pagination.type == 'scroll':
            return False
        else:
            return False
