import os
import json
import select

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm

from scraperai.models import WebpageFields, Pagination, WebpageType, ScraperConfig
from scraperai import ParserAI, Scraper
from scraperai.crawlers import SeleniumCrawler


class LocalScraperAI:
    def __init__(self, url):
        self.crawler = SeleniumCrawler()
        env_file = find_dotenv()
        if env_file:
            load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key is None:
            openai_api_key = input('Please, enter your OpenAI API key: ')

        self.parser = ParserAI(openai_api_key=openai_api_key)
        self.url = url
        self.crawler.get(url)
        # TODO: automatically accept cookies!

    def current_state(self):
        ...

    def __str__(self):
        ...

    @property
    def ipython_screenshot(self):
        return f'<img width=400 src="data:image/png;base64,{self.crawler.get_screenshot_as_base64()}" />'

    def step1(self):
        # TODO: fqdn or animation
        crawler = self.crawler
        parser = self.parser
        url = self.url

        page_type = parser.detect_page_type(page_source=crawler.page_source,
                                            screenshot=crawler.get_screenshot_as_base64())
        self.page_type = page_type
        pagination = parser.detect_pagination(crawler.page_source)
        self.pagination = pagination
        try:
            catalog_item = parser.detect_catalog_item(page_source=crawler.page_source, website_url=url, extra_prompt=None)
            self.catalog_item = catalog_item
            self.highlight_catalog_items()
        except:
            self.page_type = WebpageType.DETAILS
            catalog_item = None
        # TODO: better human-readable output
        return page_type, pagination, catalog_item

    def extract_fields_not_nested(self):
        # TODO: fqdn or animation
        fields = self.parser.extract_fields(html_snippet=self.catalog_item.html_snippet)
        self.fields = fields
        # TODO: better human-readable output (too wide now)
        self._print_fields(fields)
        self.highlight_fields()

    def extract_fields_nested(self):
        parser = self.parser
        crawler = self.crawler
        html_snippet = parser.summarize_details_page_as_valid_html(
            page_source=crawler.page_source,
            screenshot=crawler.get_screenshot_as_base64()
        )
        fields = parser.extract_fields(html_snippet)
        self.fields = fields
        self._print_fields(fields)
        self.highlight_fields()

    def step2(self, with_nested: bool = False):
        self.nested_pages = with_nested
        if self.page_type == 'catalog' and with_nested:
            self.crawler.get(self.catalog_item.urls_on_page[0])
            self.extract_fields_nested()
        if self.page_type == 'catalog' and not with_nested:
            self.extract_fields_not_nested()
        if self.page_type == 'detailed_page':
            self.extract_fields_nested()

    def step3(self):
        match self.nested_pages:
            case False:
                max_pages, max_rows = 5, 200
            case True:
                max_pages, max_rows = 2, 20
            case _:
                raise NotImplemented('Nested pages should be either True or False')

        config = ScraperConfig(
            start_url=self.url,
            page_type=self.page_type,
            pagination=self.pagination,
            catalog_item=self.catalog_item,
            open_nested_pages=self.nested_pages,
            fields=self.fields,
            max_pages=max_pages,
            max_rows=max_rows
        )
        scraper = Scraper(config, self.crawler)

        rows = []
        # TODO: better work for infinite scroll
        for item in tqdm(scraper.scrape(), total=max_rows):
            rows.append(item)

        self.rows = rows
        return self.print_rows

    @property
    def print_rows(self):
        return pd.DataFrame(self.rows).to_markdown(tablefmt='plain', index=False)

    @property
    def df_rows(self):
        return pd.DataFrame(self.rows)

    @staticmethod
    def _print_fields(fields: WebpageFields):
        print(f'Static fields ({len(fields.static_fields)}):')

        data = [{'name': f.field_name, 'xpath': f.field_xpath, 'value': f.first_value} for f in fields.static_fields]
        df = pd.DataFrame(data)
        print(df.to_markdown(tablefmt='plain', index=True))

        print()
        print(f'Dynamic fields ({len(fields.dynamic_fields)}):')
        if len(fields.dynamic_fields) == 0:
            print('Not found')
            return
        index = len(fields.static_fields)
        for field in fields.dynamic_fields:
            print(f' {index}  Section {field.section_name}\n'
                  f'    Labels xpath: {field.name_xpath}\n'
                  f'    Values xpath: {field.value_xpath}\n'
                  f'    Value: {field.first_values}')
            index += 1

    def highlight_fields(self):
        crawler = self.crawler
        fields = self.fields
        colors = ['#539878', '#5499D1', '#549B9A', '#5982A3', '#5A5499', '#68D5A2', '#75DDDC', '#8981D7', '#98D1FF',
                  '#98FFCF', '#9D5A5A', '#A05789', '#AAFFFE', '#C6C1FF', '#CD7CB3', '#D17A79', '#FAB4E4', '#FFB1B0']
        for index, field in enumerate(fields.static_fields):
            crawler.highlight_by_xpath(field.field_xpath, colors[index % len(colors)], border=4)
        for index, field in enumerate(fields.dynamic_fields):
            color = colors[index % len(colors)]
            crawler.highlight_by_xpath(field.value_xpath, color, border=3)
            crawler.highlight_by_xpath(field.name_xpath, color, border=3)

    def highlight_catalog_items(self):
        catalog_item = self.catalog_item
        crawler = self.crawler
        if catalog_item is not None:
            crawler.highlight_by_xpath(catalog_item.card_xpath, '#8981D7', 5)
            crawler.highlight_by_xpath(catalog_item.url_xpath, '#5499D1', 3)