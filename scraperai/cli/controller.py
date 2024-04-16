import datetime
import json
import os
from urllib.parse import urlparse

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from scraperai import BaseCrawler
from scraperai.cli.model import ScreenStatus
from scraperai.cli.utils import convert_ranges_to_indices, delete_fields_by_range, delete_field_by_name, DATA_DIR
from scraperai.cli.view import View
from scraperai.exceptions import NotFoundError
from scraperai.models import CatalogItem, WebpageFields, ScraperConfig, WebpageType
from scraperai import ParserAI
from scraperai.crawlers import SeleniumCrawler
from scraperai.scraper import Scraper


class Controller:
    crawler: BaseCrawler = None
    parser: ParserAI = None
    rows: list = []

    def __init__(self, start_url: str):
        self.start_url = start_url
        self.config = ScraperConfig(
            start_url=start_url,
            page_type=None,
            pagination=None,
            catalog_item=None,
            open_nested_pages=False,
            fields=WebpageFields(static_fields=[], dynamic_fields=[]),
            max_pages=1,
            max_rows=1,
            total_cost=None
        )
        self.view = View()

    @staticmethod
    def load_configs() -> list[ScraperConfig]:
        all_dirs = [DATA_DIR, './']
        files = []
        for data_dir in all_dirs:
            files += [os.path.join(data_dir, name) for name in os.listdir(data_dir) if name.endswith('.scraperai.json')]
        configs = []
        for filepath in files:
            with open(filepath, 'r') as f:
                configs.append(ScraperConfig(**json.load(f)))
        return configs

    def init_crawler(self):
        click.echo('Starting webdriver...')
        self.crawler = SeleniumCrawler()
        click.echo(f'Webdriver is ok')

    def init_scraper(self):
        self.view.show_api_key_screen(status=ScreenStatus.loading)
        env_file = find_dotenv()
        if env_file:
            load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if openai_api_key is not None:
            self.view.show_api_key_screen(status=ScreenStatus.show)
        else:
            openai_api_key, should_save = self.view.show_api_key_screen(status=ScreenStatus.edit)
            if should_save:
                with open('.env', 'w+') as f:
                    f.write(f'OPENAI_API_KEY={openai_api_key}')
        self.parser = ParserAI(openai_api_key=openai_api_key)

    def detect_page_type(self):
        self.view.show_page_type_screen(status=ScreenStatus.loading)
        self.crawler.get(self.start_url)
        screenshot = None
        if isinstance(self.crawler, SeleniumCrawler):
            screenshot = self.crawler.get_screenshot_as_base64()
        page_type = self.parser.detect_page_type(
            page_source=self.crawler.page_source,
            screenshot=screenshot
        )
        self.view.show_page_type_screen(status=ScreenStatus.show, page_type=page_type)

        page_type = self.view.show_page_type_screen(status=ScreenStatus.edit, page_type=page_type)
        self.config.page_type = page_type

    def detect_pagination(self):
        self.view.show_pagination_screen(status=ScreenStatus.loading)
        self.crawler.get(self.start_url)
        pagination = self.parser.detect_pagination(page_source=self.crawler.page_source)
        self.view.show_pagination_screen(status=ScreenStatus.show, pagination=pagination)
        pagination = self.view.show_pagination_screen(status=ScreenStatus.edit, pagination=pagination)
        self.config.pagination = pagination

    def detect_catalog_item(self, extra_prompt: str = None, catalog_item: CatalogItem = None):
        self.view.show_card_screen(status=ScreenStatus.loading)
        if catalog_item is None:
            try:
                self.crawler.get(self.start_url)
                catalog_item = self.parser.detect_catalog_item(page_source=self.crawler.page_source,
                                                               website_url=self.start_url,
                                                               extra_prompt=extra_prompt)
            except NotFoundError:
                catalog_item = None
        self.view.show_card_screen(status=ScreenStatus.show, catalog_item=catalog_item)
        # Highlight cards
        if catalog_item and isinstance(self.crawler, SeleniumCrawler):
            self.crawler.highlight_by_xpath(catalog_item.card_xpath, '#8981D7', 5)
            self.crawler.highlight_by_xpath(catalog_item.url_xpath, '#5499D1', 3)

        edit_form = self.view.show_card_screen(status=ScreenStatus.edit, catalog_item=catalog_item)
        if edit_form.has_changes:
            if edit_form.user_suggestion:
                if catalog_item is not None:
                    extra_prompt = f'You have made a mistake.' \
                                   f'{catalog_item.card_xpath} is not a correct xpath of catalog card. ' \
                                   f'I can give you following instruction: {edit_form.user_suggestion}'
                else:
                    extra_prompt = f'I can give you following instruction: {edit_form.user_suggestion}'
                return self.detect_catalog_item(extra_prompt)
            else:
                catalog_item = self.parser.manually_change_catalog_item(self.crawler.page_source,
                                                                        edit_form.new_card_xpath,
                                                                        edit_form.new_url_xpath,
                                                                        website_url=self.start_url)
                return self.detect_catalog_item(catalog_item=catalog_item)

        if catalog_item is None:
            self.quit('Could not find catalog item. Aborting...')
        self.config.catalog_item = catalog_item

    def _highlight_fields(self, fields: WebpageFields):
        if not isinstance(self.crawler, SeleniumCrawler):
            return

        colors = ['#539878', '#5499D1', '#549B9A', '#5982A3', '#5A5499', '#68D5A2', '#75DDDC', '#8981D7', '#98D1FF',
                  '#98FFCF', '#9D5A5A', '#A05789', '#AAFFFE', '#C6C1FF', '#CD7CB3', '#D17A79', '#FAB4E4', '#FFB1B0']
        for index, field in enumerate(fields.static_fields):
            self.crawler.highlight_by_xpath(field.field_xpath, colors[index % len(colors)], border=4)
        for index, field in enumerate(fields.dynamic_fields):
            color = colors[index % len(colors)]
            self.crawler.highlight_by_xpath(field.value_xpath, color, border=3)
            self.crawler.highlight_by_xpath(field.name_xpath, color, border=3)

    def detect_fields(self, *, nested_page_url: str = None, html_snippet: str = None):
        self.view.show_fields_screen(status=ScreenStatus.loading)
        if nested_page_url is not None:
            self.crawler.get(nested_page_url)
            screenshot = None
            if isinstance(self.crawler, SeleniumCrawler):
                screenshot = self.crawler.get_screenshot_as_base64()
            html_snippet = self.parser.summarize_details_page_as_valid_html(
                page_source=self.crawler.page_source,
                screenshot=screenshot
            )
            fields = self.parser.extract_fields(html_snippet)
        elif html_snippet is not None:
            fields = self.parser.extract_fields(html_snippet)
        else:
            raise ValueError
        self.view.show_fields_screen(status=ScreenStatus.show, fields=fields)
        self._highlight_fields(fields)
        while True:
            edit_form = self.view.show_fields_screen(status=ScreenStatus.edit, fields=fields)
            if not edit_form.has_changes:
                break

            if edit_form.action_type == 'a':
                self.view.show_fields_screen(status=ScreenStatus.loading)
                new_fields = self.parser.find_fields(html_snippet, edit_form.user_suggestion)
                if new_fields.is_empty:
                    self.view.show_fields_screen(status=ScreenStatus.show, not_found_message='Nothing found')
                else:
                    fields.static_fields += new_fields.static_fields
                    fields.dynamic_fields += new_fields.dynamic_fields
                    self.view.show_fields_screen(status=ScreenStatus.show, fields=fields)
                    self._highlight_fields(fields)
            else:
                try:
                    range_to_delete = convert_ranges_to_indices(edit_form.field_to_delete)
                    deleted = delete_fields_by_range(fields, range_to_delete)
                except ValueError:
                    field_name_to_delete = edit_form.field_to_delete
                    deleted = delete_field_by_name(fields, field_name_to_delete)
                if deleted:
                    self.view.show_fields_screen(status=ScreenStatus.show, fields=fields)
                    self._highlight_fields(fields)
                else:
                    self.view.show_fields_screen(status=ScreenStatus.show, not_found_message='No such field')

        self.config.fields = fields

    def scrape(self):
        scraper = Scraper(self.config, self.crawler)
        if self.config.page_type == WebpageType.OTHER:
            self.quit('Unsupported page type. Aborting...')
            return
        elif self.config.page_type == WebpageType.DETAILS:
            rows = []
            for row in scraper.scrape_nested_items([self.start_url]):
                rows.append(row)
        else:
            if self.config.open_nested_pages:
                urls: set[str] = set()
                with View.progressbar(iterable=scraper.scrape_nested_items_urls(),
                                      length=self.config.max_rows,
                                      label='Collecting nested urls') as bar:
                    for url in bar:
                        urls.add(url)
                        bar.update(1)
                click.echo(f'Collected {len(urls)} urls to nested pages')
                rows = []
                with View.progressbar(iterable=scraper.scrape_nested_items(urls),
                                      length=self.config.max_rows,
                                      label='Scraping nested pages') as bar:
                    for row in bar:
                        rows.append(row)
            else:
                rows = []
                with View.progressbar(iterable=scraper.scrape_catalog_items(),
                                      length=self.config.max_rows,
                                      label='Scraping catalog pages') as bar:
                    for row in bar:
                        rows.append(row)

        self.rows = rows

    def export_results(self):
        self.view.show_export_screen(status=ScreenStatus.loading, data_size=len(self.rows))
        # TODO: Add data postprocessing

        self.view.show_export_screen(status=ScreenStatus.show)

        is_first_iteration = True
        while True:
            output_format = self.view.show_export_screen(status=ScreenStatus.edit, force_yes=is_first_iteration)
            is_first_iteration = False
            if output_format is None:
                break
            # Export logic
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'results_{timestamp}.{output_format}'
            if output_format == 'json':
                with open(filename, 'w+') as f:
                    json.dump(self.rows, f, indent=4, ensure_ascii=False)
            elif output_format == 'xlsx':
                df = pd.DataFrame(self.rows)
                df.to_excel(filename)
            elif output_format == 'csv':
                df = pd.DataFrame(self.rows)
                df.to_csv(filename)

            self.view.show_export_screen(status=ScreenStatus.show, filename=filename)

    def run(self):
        # Step 1: Start crawler
        self.init_crawler()

        # Step 2: Get openai token and init scraper
        self.init_scraper()

        # Step 3: Search for existing configs
        configs = self.load_configs()
        loaded_from_memory = False
        for config in configs:
            if config.start_url == self.start_url:
                should_use = self.view.show_configs_search_screen(config)
                if should_use:
                    loaded_from_memory = True
                    self.config = config
                    break

        # Step 4: Detect page type
        if not loaded_from_memory:
            while self.config.page_type is None or self.config.page_type == WebpageType.CAPTCHA:
                self.detect_page_type()
                if self.config.page_type == WebpageType.OTHER:
                    self.quit(f'Unsupported page type {self.config.page_type}. Aborting...')
                if self.config.page_type == WebpageType.CAPTCHA:
                    if not self.view.show_captcha_warning():
                        self.quit()

            if self.config.page_type == WebpageType.CATALOG:
                # Step 5: Detect pagination
                self.detect_pagination()
                # Step 6: Detect catalog item
                self.detect_catalog_item()
                # Step 7: Detect fields
                self.config.open_nested_pages = self.view.show_open_nested_pages_screen()
                if self.config.open_nested_pages:
                    self.detect_fields(nested_page_url=self.config.catalog_item.urls_on_page[0])
                else:
                    self.detect_fields(html_snippet=self.config.catalog_item.html_snippet)
            else:
                # Step 7: Detect fields
                self.detect_fields(nested_page_url=self.start_url)

        # Step 8: Ask for limits
        if self.config.page_type == WebpageType.CATALOG:
            max_pages, max_rows = self.view.show_limits_screen()
            self.config.max_rows = max_rows
            self.config.max_pages = max_pages

        # Step 8: Scraping all pages accroding to the task
        self.view.show_config_screen(self.config, self.parser.total_cost)
        should_save_config = self.view.show_config_save_screen()
        if should_save_config:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name = urlparse(self.config.start_url).netloc
            filename = f'{name}_{timestamp}.scraperai.json'
            with open(filename, 'w+') as f:
                f.write(self.config.model_dump_json())
        self.scrape()
        self.export_results()
        self.quit('Thank you for using ScraperAI!')

    def quit(self, message: str = None, exit_code: int = 0):
        if message:
            click.echo(message)
        if isinstance(self.crawler, SeleniumCrawler):
            self.crawler.driver.quit()
        exit(exit_code)
