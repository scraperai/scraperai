import logging
import time

from pydantic import BaseModel
from lxml import html

from scraperai.crawlers import BaseCrawler, SeleniumCrawler
from scraperai.lm.base import BaseLM
from scraperai.lm.openai import OpenAI, JsonOpenAI
from scraperai.parsers import (
    PaginationDetector,
    Pagination,
    WebpageType,
    WebpageVisionClassifier,
    WebpageTextClassifier,
    WebpagePartsDescriptor,
    WebpageVisionDescriptor,
    CatalogItemDetector, DataFieldsExtractor
)
from scraperai.parsers.models import WebpageFields, CatalogItem
from scraperai.parsers.utils import extract_fields_from_html, extract_items
from scraperai.utils import fix_relative_url
from scraperai.utils.image import compress_b64_image
from scraperai.vision.base import BaseVision
from scraperai.vision.openai import VisionOpenAI

logger = logging.getLogger(__file__)


class ScrapingTask(BaseModel):
    start_url: str
    pagination: Pagination
    catalog_item: CatalogItem
    open_nested_pages: bool
    fields: WebpageFields


class ScraperAI:
    def __init__(self,
                 crawler: BaseCrawler = None,
                 lm_model: BaseLM = None,
                 json_lm_model: JsonOpenAI = None,
                 vision_model: BaseVision = None,
                 openai_api_key: str = None,
                 openai_organization: str = None):
        if crawler is None:
            self.crawler = SeleniumCrawler()
        else:
            self.crawler = crawler

        if lm_model is None:
            self.lm_model = OpenAI(openai_api_key, openai_organization, temperature=0)
        else:
            self.lm_model = lm_model

        if json_lm_model is None:
            self.json_lm_model = JsonOpenAI(openai_api_key, openai_organization, temperature=0)
        else:
            self.json_lm_model = json_lm_model

        if vision_model is None:
            self.vision_model = VisionOpenAI(openai_api_key, openai_organization, temperature=0)
        else:
            self.vision_model = vision_model

    @property
    def total_cost(self) -> float:
        cost = 0.0
        if isinstance(self.lm_model, OpenAI):
            cost += self.lm_model.total_cost
        if isinstance(self.json_lm_model, JsonOpenAI):
            cost += self.json_lm_model.total_cost
        if isinstance(self.vision_model, VisionOpenAI):
            cost += self.vision_model.total_cost
        return cost

    def detect_page_type(self, url: str) -> WebpageType:
        self.crawler.get(url)
        try:
            screenshot = self.crawler.get_screenshot_as_base64()
        except NotImplementedError:
            screenshot = None
        if screenshot:
            screenshot = compress_b64_image(screenshot, aspect_ratio=0.5)
            return WebpageVisionClassifier(model=self.vision_model).classify(screenshot)
        else:
            return WebpageTextClassifier(model=self.lm_model).classify(self.crawler.page_source)

    def detect_pagination(self, url: str) -> Pagination:
        self.crawler.get(url)
        html_content = self.crawler.page_source
        pagination = PaginationDetector(model=self.lm_model).find_pagination(html_content)
        return pagination

    def detect_catalog_item(self, url: str, extra_prompt: str = None) -> CatalogItem | None:
        self.crawler.get(url)
        html_content = self.crawler.page_source
        detector = CatalogItemDetector(model=self.json_lm_model)
        item = detector.detect_catalog_item(html_content, extra_prompt)
        item.urls_on_page = [fix_relative_url(url, u) for u in item.urls_on_page]
        return item

    def manually_change_catalog_item(self, url: str, card_xpath: str, url_xpath: str):
        self.crawler.get(url)
        html_content = self.crawler.page_source
        detector = CatalogItemDetector(model=self.json_lm_model)
        item = detector.manually_change_catalog_item(html_content, card_xpath, url_xpath)
        item.urls_on_page = [fix_relative_url(url, u) for u in item.urls_on_page]
        return item

    def extract_fields(self, html_snippet: str) -> WebpageFields:
        return DataFieldsExtractor(model=self.lm_model).extract_fields(html_snippet)

    def find_fields(self, html_snippet: str, user_description: str) -> WebpageFields:
        context = f"IMPORTANT! Search for fields that are described in " \
                  f"the following very important instructions: {user_description}"
        return DataFieldsExtractor(model=self.lm_model).find_fields(html_snippet, context)

    def summarize_details_page_as_valid_html(self, url: str) -> str:
        self.crawler.get(url)
        html_content = self.crawler.page_source
        # Generate webpage description to give GPT some context
        try:
            screenshot = self.crawler.get_screenshot_as_base64()
        except NotImplementedError:
            screenshot = None
        if screenshot:
            description = WebpageVisionDescriptor(model=self.vision_model).describe(screenshot)
        else:
            description = None

        # Split html into prieces, describe each piece, mark pieces as relevant/irrelevant,
        # remove irrelevant pieces and return new html
        parts_descriptor = WebpagePartsDescriptor(model=self.json_lm_model)
        return parts_descriptor.find_and_remove_irrelevant_html_parts(html_content, context=description)

    def _switch_page(self, pagination: Pagination) -> bool:
        if pagination.type == 'xpath':
            try:
                self.crawler.click(pagination.xpath)
                time.sleep(3)
                return True
            except Exception as e:
                logger.exception(e)
                return False
        elif pagination.type == 'url_param':
            raise NotImplementedError()
        elif pagination.type == 'scroll':
            raise NotImplementedError()
        else:
            raise ValueError

    def collect_data_from_catalog_pages(self,
                                        start_url: str,
                                        pagination: Pagination,
                                        catalog_item_xpath: str,
                                        fields: WebpageFields,
                                        max_pages: int,
                                        max_rows: int) -> list[dict]:
        all_items = []
        page_number = 0
        self.crawler.get(start_url)
        while True:
            items = extract_items(self.crawler.page_source, fields, catalog_item_xpath)
            all_items += items
            logger.info(f'Page: {page_number}: Found {len(items)} new cards')

            success = self._switch_page(pagination)
            if not success:
                break

            page_number += 1
            if page_number >= max_pages or len(all_items) >= max_rows:
                break

        logger.info(f'Totally found {len(all_items)} cards')
        return all_items

    def collect_urls_to_nested_pages(self,
                                     start_url: str,
                                     pagination: Pagination,
                                     url_xpath: str,
                                     max_pages: int = 3) -> list[str]:
        urls = set()
        page_number = 0
        self.crawler.get(start_url)
        while True:
            tree = html.fromstring(self.crawler.page_source)
            new_urls = [fix_relative_url(start_url, url) for url in tree.xpath(url_xpath)]
            urls.update(new_urls)
            logger.info(f'Page: {page_number}: Found {len(new_urls)} new urls')
            success = self._switch_page(pagination)
            if not success:
                break
            page_number += 1
            if page_number >= max_pages:  # TODO: Remove this
                break

        logger.info(f'Totally found {len(urls)} urls')
        return list(urls)

    def collect_data_from_nested_pages(self, urls: list[str], fields: WebpageFields) -> list[dict]:
        urls = urls[0:10]  # TODO: Remove this
        items = []
        for url in urls:
            self.crawler.get(url)
            data = extract_fields_from_html(self.crawler.page_source, fields)
            items.append(data)
        return items
