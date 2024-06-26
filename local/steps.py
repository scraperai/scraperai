import os

import pandas as pd
from dotenv import find_dotenv, load_dotenv
from tqdm import tqdm
from IPython import display

from scraperai.models import WebpageFields, Pagination, WebpageType, ScraperConfig
from scraperai import ParserAI, Scraper
from scraperai.crawlers import SeleniumCrawler
from scraperai.utils.cat_progress_bar import cat_animation


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

        self.config = ScraperConfig(
            start_url=url,
            page_type=None,
            pagination=Pagination(type='none'),
            catalog_item=None,
            open_nested_pages=False,
            fields=WebpageFields(static_fields=[], dynamic_fields=[]),
            max_pages=1,
            max_rows=1,
            total_cost=None
        )
        self.rows = None

    def current_state(self):
        ...

    def __str__(self):
        ...

    @property
    def ipython_screenshot(self):
        data = self.crawler.get_screenshot_as_base64(zoom_out=False)
        return display.HTML(f'<img width=600 src="data:image/png;base64,{data}" />')

    @property
    def summary(self) -> str:
        config = self.config
        items = [['Start url', config.start_url]]
        if config.page_type:
            items.append(['Page Type', str(config.page_type)])
        if config.pagination:
            items.append(['Pagination', str(config.pagination)])
        if config.catalog_item:
            items.append(['Catalog Item', f'(card_xpath={config.catalog_item.card_xpath}, url_xpath={config.catalog_item.url_xpath})'])
        if len(config.fields.static_fields) > 0 or len(config.fields.dynamic_fields) > 0:
            items.append(['Fields', f'{len(config.fields.static_fields)} static, {len(config.fields.dynamic_fields)} dynamic'])
        if config.max_pages > 1 and config.max_rows > 1:
            items.append(['Max pages', config.max_pages])
            items.append(['Max rows', config.max_rows])
        if self.parser.total_cost:
            items.append(['Total OpenAI cost, $', f'{self.parser.total_cost:.3f}'])
        df = pd.DataFrame(items)
        text = df.to_markdown(tablefmt='plain', index=False)
        return 'Summary:\n' + '\n'.join(text.split('\n')[1:])

    @cat_animation()
    def step1(self):
        crawler = self.crawler
        parser = self.parser
        url = self.url

        page_type = parser.detect_page_type(page_source=crawler.page_source,
                                            screenshot=crawler.get_screenshot_as_base64())
        self.config.page_type = page_type
        if page_type == WebpageType.CATALOG:
            self.config.pagination = parser.detect_pagination(crawler.page_source)
        else:
            self.config.pagination = Pagination(type='scroll')
        try:
            catalog_item = parser.detect_catalog_item(page_source=crawler.page_source, website_url=url, extra_prompt=None)
            self.config.catalog_item = catalog_item
            self.highlight_catalog_items()
        except Exception as e:
            self.config.page_type = WebpageType.DETAILS

    def extract_fields_not_nested(self):
        fields = self.parser.extract_fields(html_snippet=self.config.catalog_item.html_snippet)
        self.config.fields = fields
        # TODO: better human-readable output (too wide now)
        self.highlight_fields()

    def extract_fields_nested(self):
        parser = self.parser
        crawler = self.crawler
        html_snippet = parser.summarize_details_page_as_valid_html(
            page_source=crawler.page_source,
            screenshot=crawler.get_screenshot_as_base64()
        )
        fields = parser.extract_fields(html_snippet)
        self.config.fields = fields
        self.highlight_fields()

    @cat_animation()
    def step2(self, with_nested: bool = False):
        self.config.open_nested_pages = with_nested
        if self.config.page_type == 'catalog' and with_nested:
            self.crawler.get(self.config.catalog_item.urls_on_page[0])
            self.extract_fields_nested()
        if self.config.page_type == 'catalog' and not with_nested:
            self.extract_fields_not_nested()
        if self.config.page_type == 'detailed_page':
            self.extract_fields_nested()

    def step3(self) -> pd.DataFrame:
        match self.config.open_nested_pages:
            case False:
                max_pages, max_rows = 5, 200
            case True:
                max_pages, max_rows = 2, 20
            case _:
                raise NotImplemented('Nested pages should be either True or False')

        self.config.max_pages = max_pages
        self.config.max_rows = max_rows
        scraper = Scraper(self.config, self.crawler)

        rows = []
        # TODO: better work for infinite scroll
        for item in tqdm(scraper.scrape(), total=max_rows):
            rows.append(item)

        self.rows = rows
        return self.df_rows

    @property
    def df_rows(self):
        return pd.DataFrame(self.rows)

    @property
    def static_fields_df(self) -> pd.DataFrame | None:
        fields = self.config.fields
        static_data = [
            {'name': f.field_name, 'xpath': f.field_xpath, 'value': f.first_value}
            for f in fields.static_fields
        ]
        return pd.DataFrame(static_data)

    @property
    def dynamic_fields_df(self) -> pd.DataFrame | None:
        fields = self.config.fields
        dynamic_data = [
            {
                'section': f.section_name,
                'name_xpath': f.name_xpath,
                'value_xpath': f.value_xpath,
                'values': f.first_values
            }
            for f in fields.dynamic_fields
        ]
        return pd.DataFrame(dynamic_data)

    def highlight_fields(self):
        crawler = self.crawler
        fields = self.config.fields
        for index, field in enumerate(fields.static_fields):
            crawler.highlight_by_xpath(field.field_xpath, field.color, border=4)
        for index, field in enumerate(fields.dynamic_fields):
            crawler.highlight_by_xpath(field.value_xpath, field.color, border=3)
            crawler.highlight_by_xpath(field.name_xpath, field.color, border=3)

    def highlight_catalog_items(self):
        catalog_item = self.config.catalog_item
        crawler = self.crawler
        if catalog_item is not None:
            crawler.highlight_by_xpath(catalog_item.card_xpath, '#8981D7', 5)
            crawler.highlight_by_xpath(catalog_item.url_xpath, '#5499D1', 3)