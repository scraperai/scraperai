import logging
from abc import ABC, abstractmethod
from typing import Generator, Iterable

from lxml import html

from scraperai.parsers.models import WebpageFields, Pagination
from scraperai.parsers.utils import extract_fields_from_html, extract_items
from scraperai.utils import fix_relative_url

logger = logging.getLogger(__file__)


class BaseCrawler(ABC):
    @abstractmethod
    def get(self, url: str):
        ...

    @property
    @abstractmethod
    def page_source(self) -> str:
        ...

    @abstractmethod
    def click(self, xpath: str) -> None:
        ...

    @abstractmethod
    def get_screenshot_as_base64(self) -> str:
        raise NotImplementedError()

    @abstractmethod
    def switch_page(self, pagination: Pagination) -> bool:
        raise NotImplementedError()

    def iter_data_from_catalog_pages(self,
                                     start_url: str,
                                     pagination: Pagination,
                                     catalog_item_xpath: str,
                                     fields: WebpageFields,
                                     max_pages: int,
                                     max_rows: int) -> Generator[list[dict], None, None]:
        total_count = 0
        page_number = 0
        self.get(start_url)
        while True:
            items = extract_items(self.page_source, fields, catalog_item_xpath)
            total_count += len(items)
            yield items
            logger.info(f'Page: {page_number}: Found {len(items)} new cards')

            success = self.switch_page(pagination)
            if not success:
                break

            page_number += 1
            if page_number >= max_pages or total_count >= max_rows:
                break

    def iter_urls_to_nested_pages(self,
                                  start_url: str,
                                  pagination: Pagination,
                                  url_xpath: str,
                                  max_pages: int = 3) -> Generator[list[str], None, None]:
        page_number = 0
        self.get(start_url)
        while True:
            tree = html.fromstring(self.page_source)
            new_urls = [fix_relative_url(start_url, url) for url in tree.xpath(url_xpath)]
            logger.info(f'Page: {page_number}: Found {len(new_urls)} new urls')
            yield new_urls

            success = self.switch_page(pagination)
            if not success:
                break
            page_number += 1
            if page_number >= max_pages:
                break

    def iter_data_from_nested_pages(self,
                                    urls: Iterable[str],
                                    fields: WebpageFields,
                                    max_rows: int = 1000) -> Generator[dict, None, None]:
        for url in list(urls)[:max_rows]:
            self.get(url)
            yield extract_fields_from_html(self.page_source, fields)
