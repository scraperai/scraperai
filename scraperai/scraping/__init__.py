import time
import logging

import pandas as pd
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from lxml import etree
from selenium.webdriver.common.by import By
from tqdm import tqdm

from scraperai.webdriver.manager import WebdriversManager
from scraperai.llm.chat import OpenAIChatModel, OpenAIModel
from scraperai.parsing.pagination import PaginationDetection
from scraperai.parsing.catalog import CatalogParser
from scraperai.parsing.details import DetailsPageParser
from scraperai.utils import prettify_table


logger = logging.getLogger(__file__)


def fix_relative_url(base_url: str, url: str) -> str:
    if url.startswith('http'):
        return url
    return base_url + url.lstrip('/')


class SimpleScrapingFlow:
    def __init__(self, api_key: str,
                 model: OpenAIModel,
                 webmanager: WebdriversManager,
                 active_session_url: str = None,
                 active_session_id: str = None):
        chat_model = OpenAIChatModel(api_key, model)
        self.pagination_detector = PaginationDetection(chat_model=chat_model)
        self.catalog_parser = CatalogParser(chat_model=chat_model)
        self.details_parser = DetailsPageParser(chat_model=chat_model)
        self.webmanager = webmanager

        if active_session_id:
            self.driver = self.webmanager.from_session_id(active_session_url, active_session_id)
        else:
            self.driver = self.webmanager.create_driver()

    def collect_all_data(self, start_url: str) -> pd.DataFrame:
        logger.info(f'Start parsing "{start_url}"')

        # Get catalog page
        components = urlparse(start_url)
        base_url = components.scheme + '://' + components.netloc + '/'
        self.driver.get(start_url)
        time.sleep(1)

        # Find pagination
        pagination_xpath = self.pagination_detector.find_pagination(self.driver.page_source)
        if pagination_xpath:
            logger.info(f'Pagination xpath was found: "{pagination_xpath}"')
        else:
            logger.info('Pagination was not found')

        # Find urls selectors
        classnames = self.catalog_parser.find_classnames(self.driver.page_source,
                                                         search_elements=['name', 'url'])
        url_classname = classnames['url']
        logger.info(f'Found url classname: "{url_classname}"')

        # Iter pages
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
            if page_number >= 3:
                break

        # Iter details pages
        logger.info(f'Totally found {len(urls)} urls')
        urls = list(urls)
        urls = urls[0:10]
        items = []
        selectors = None
        for i in tqdm(range(len(urls))):
            self.driver.get(urls[i])
            time.sleep(1)
            if selectors is None:
                selectors = self.details_parser.to_selectors(self.driver.page_source)
                if selectors is None:
                    return pd.DataFrame({'urls': urls})

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
