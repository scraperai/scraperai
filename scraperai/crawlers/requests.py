import requests

from scraperai.crawlers.base import BaseCrawler
from scraperai.models import Pagination
from scraperai.utils import get_url_query_param_value, add_or_replace_url_param


class RequestsCrawler(BaseCrawler):
    current_url: str = None

    def __init__(self):
        self.__page_source = None

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
        if pagination.type == 'xpath':
            return False
        elif pagination.type == 'url_param':
            params = get_url_query_param_value(self.current_url, pagination.url_param)
            if params is None:
                new_page = pagination.url_param_first_value
            else:
                new_page = int(params[0]) + 1
            new_url = add_or_replace_url_param(self.current_url, pagination.url_param, new_page)
            self.get(new_url)
            # TODO: How to stop pagination?
            return True
        elif pagination.type == 'scroll':
            return False
        else:
            raise TypeError
