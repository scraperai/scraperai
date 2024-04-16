import logging
from typing import Generator, Iterable

from lxml import html, etree

from scraperai import BaseCrawler
from scraperai.models import ScraperConfig, WebpageType
from scraperai.parsers.utils import extract_fields_from_html, extract_fields_from_tree
from scraperai.utils import fix_relative_url

logger = logging.getLogger('scraperai')


class Scraper:
    def __init__(self, config: ScraperConfig, crawler: BaseCrawler):
        self.config = config
        self.crawler = crawler

    def scrape(self) -> Generator[dict, None, None]:
        if self.config.page_type == WebpageType.DETAILS:
            for row in self.scrape_nested_items([self.config.start_url]):
                yield row
        elif self.config.page_type == WebpageType.CATALOG:
            if self.config.open_nested_pages:
                urls = list(self.scrape_nested_items_urls())
                for row in self.scrape_nested_items(urls):
                    yield row
            else:
                for row in self.scrape_catalog_items():
                    yield row
        else:
            logger.error(f'Unsupported page type: {self.config.page_type}')

    def scrape_catalog_items(self) -> Generator[dict, None, None]:
        total_count = 0
        page_number = 0
        self.crawler.get(self.config.start_url)
        while True:
            count = 0
            tree = html.fromstring(self.crawler.page_source)
            for node in tree.xpath(self.config.catalog_item.card_xpath):
                n = html.fragment_fromstring(
                    etree.tostring(node, pretty_print=False, method="html", encoding='unicode'),
                    create_parent=True
                )
                data = extract_fields_from_tree(n, self.config.fields, select_context_node=True)
                count += 1
                yield data

            total_count += count
            logger.debug(f'Page: {page_number}: Found {count} new items')

            success = self.crawler.switch_page(self.config.pagination)
            if not success:
                break

            page_number += 1
            if page_number >= self.config.max_pages or total_count >= self.config.max_rows:
                break

    def scrape_nested_items_urls(self) -> Generator[str, None, None]:
        page_number = 0
        self.crawler.get(self.config.start_url)
        while True:
            tree = html.fromstring(self.crawler.page_source)
            for url in tree.xpath(self.config.catalog_item.url_xpath):
                yield fix_relative_url(self.config.start_url, url)

            success = self.crawler.switch_page(self.config.pagination)
            if not success:
                break
            page_number += 1
            if page_number >= self.config.max_pages:
                break

    def scrape_nested_items(self, urls: Iterable[str]) -> Generator[dict, None, None]:
        for index, url in enumerate(urls):
            if index >= self.config.max_rows:
                break
            self.crawler.get(url)
            yield extract_fields_from_html(self.crawler.page_source, self.config.fields)
