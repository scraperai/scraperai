import requests

from scraperai.crawlers.base import BaseCrawler


class RequestsCrawler(BaseCrawler):
    def __init__(self):
        self.__page_source = None

    def get(self, url: str):
        self.__page_source = requests.get(url).text

    @property
    def page_source(self) -> str:
        return self.__page_source

    def click(self, xpath: str) -> None:
        raise NotImplementedError()

    def get_screenshot_as_base64(self) -> str:
        raise NotImplementedError()
