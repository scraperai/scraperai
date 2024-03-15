import datetime
import json
import os

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from scraperai import BaseCrawler
from scraperai.cli.model import ScreenStatus
from scraperai.cli.view import View
from scraperai.exceptions import NotFoundError
from scraperai.parsers import WebpageType, Pagination
from scraperai.parsers.models import CatalogItem, WebpageFields
from scraperai.scraper import ScraperAI, ScrapingSummary
from scraperai.crawlers import SeleniumCrawler


class Controller:
    crawler: BaseCrawler = None
    scraper: ScraperAI = None
    page_type: WebpageType = None
    pagination: Pagination = None
    catalog_item: CatalogItem = None
    fields: WebpageFields = None
    open_nested_pages: bool = False
    max_pages: int = 1
    max_rows: int = 1
    rows: list = []

    def __init__(self, start_url: str):
        self.start_url = start_url
        self.view = View()

    @property
    def summary_model(self) -> ScrapingSummary:
        return ScrapingSummary(
            start_url=self.start_url,
            page_type=self.page_type,
            pagination=self.pagination,
            catalog_item=self.catalog_item,
            open_nested_pages=self.open_nested_pages,
            fields=self.fields,
            max_pages=self.max_pages,
            max_rows=self.max_rows,
            total_cost=self.scraper.total_cost
        )

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
            openai_api_key = self.view.show_api_key_screen(status=ScreenStatus.edit)

        self.scraper = ScraperAI(crawler=self.crawler, openai_api_key=openai_api_key)

    def detect_page_type(self):
        self.view.show_page_type_screen(status=ScreenStatus.loading)
        page_type = self.scraper.detect_page_type(self.start_url)
        self.view.show_page_type_screen(status=ScreenStatus.show, page_type=page_type)

        page_type = self.view.show_page_type_screen(status=ScreenStatus.edit, page_type=page_type)
        self.page_type = page_type

    def detect_pagination(self):
        self.view.show_pagination_screen(status=ScreenStatus.loading)
        pagination = self.scraper.detect_pagination(self.start_url)
        self.view.show_pagination_screen(status=ScreenStatus.show, pagination=pagination)
        pagination = self.view.show_pagination_screen(status=ScreenStatus.edit, pagination=pagination)
        self.pagination = pagination

    def detect_catalog_item(self, extra_prompt: str = None, catalog_item: CatalogItem = None) -> CatalogItem:
        self.view.show_card_screen(status=ScreenStatus.loading)
        if catalog_item is None:
            try:
                catalog_item = self.scraper.detect_catalog_item(self.start_url, extra_prompt)
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
                catalog_item = self.scraper.manually_change_catalog_item(self.start_url,
                                                                         edit_form.new_card_xpath,
                                                                         edit_form.new_url_xpath)
                return self.detect_catalog_item(catalog_item=catalog_item)

        if catalog_item is None:
            self.quit('Could not find catalog item. Aborting...')
        self.catalog_item = catalog_item
        return catalog_item

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
            html_snippet = self.scraper.summarize_details_page_as_valid_html(nested_page_url)
            fields = self.scraper.extract_fields(html_snippet)
        elif html_snippet is not None:
            fields = self.scraper.extract_fields(html_snippet)
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
                new_fields = self.scraper.find_fields(html_snippet, edit_form.user_suggestion)
                if new_fields.is_empty:
                    self.view.show_fields_screen(status=ScreenStatus.show, not_found_message='Nothing found')
                else:
                    fields.static_fields += new_fields.static_fields
                    fields.dynamic_fields += new_fields.dynamic_fields
                    self.view.show_fields_screen(status=ScreenStatus.show, fields=fields)
                    self._highlight_fields(fields)
            else:
                field_name = edit_form.field_to_delete
                deleted = False
                offset_index = len(fields.static_fields)
                for i in range(len(fields.static_fields)):
                    if fields.static_fields[i].field_name == field_name or str(i) == field_name:
                        del fields.static_fields[i]
                        deleted = True
                        break
                for i in range(len(fields.dynamic_fields)):
                    curr_index = str(i + offset_index)
                    if fields.dynamic_fields[i].section_name == field_name or curr_index == field_name:
                        del fields.dynamic_fields[i]
                        deleted = True
                        break
                if deleted:
                    self.view.show_fields_screen(status=ScreenStatus.show, fields=fields)
                    self._highlight_fields(fields)
                else:
                    self.view.show_fields_screen(status=ScreenStatus.show, not_found_message='No such field')

        self.fields = fields

    def scrape(self):
        if self.page_type == WebpageType.OTHER:
            self.quit('Unsupported page type. Aborting...')
            return
        elif self.page_type == WebpageType.DETAILS:
            rows = []
            for row in self.scraper.iter_data_from_nested_pages([self.start_url], self.fields):
                rows.append(row)
        else:
            if self.open_nested_pages:
                urls: set[str] = set()

                urls_iterator = self.scraper.iter_urls_to_nested_pages(
                    self.start_url,
                    self.pagination,
                    self.catalog_item.url_xpath,
                    self.max_pages
                )
                with View.progressbar(length=self.max_pages, label='Collecting nested urls') as bar:
                    for url_list in urls_iterator:
                        urls.update(url_list)
                        bar.update(1)
                click.echo(f'Collected {len(urls)} urls to nested pages')
                rows = []
                data_iterator = self.scraper.iter_data_from_nested_pages(urls, self.fields, self.max_rows)
                with View.progressbar(data_iterator, length=self.max_rows, label='Scraping nested pages') as bar:
                    for row in bar:
                        rows.append(row)
            else:
                rows = []
                data_iterator = self.scraper.iter_data_from_catalog_pages(
                    self.start_url,
                    self.pagination,
                    self.catalog_item.card_xpath,
                    self.fields,
                    self.max_pages,
                    self.max_rows
                )
                with View.progressbar(length=self.max_rows, label='Scraping catalog pages') as bar:
                    for data_list in data_iterator:
                        rows += data_list
                        bar.update(len(data_list))

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

        # Step 3: Detect page type
        self.detect_page_type()

        if self.page_type == WebpageType.CAPTCHA:
            self.view.show_captcha_warning()
        elif self.page_type == WebpageType.CATALOG:
            # Step 4: Detect pagination
            self.detect_pagination()
            # Step 5: Detect catalog item
            self.detect_catalog_item()
            # Step 6: Detect fields
            self.open_nested_pages = self.view.show_open_nested_pages_screen()
            if self.open_nested_pages:
                self.detect_fields(nested_page_url=self.catalog_item.urls_on_page[0])
            else:
                self.detect_fields(html_snippet=self.catalog_item.html_snippet)

            # Step 7: Ask for limits
            self.max_pages, self.max_rows = self.view.show_limits_screen()
        elif self.page_type == WebpageType.DETAILS:
            self.detect_fields(nested_page_url=self.start_url)
        else:
            self.quit(f'Unsupported page type {self.page_type}. Aborting...')

        # Step 8: Scraping all pages accroding to the task
        self.view.show_summary_screen(self.summary_model)
        self.scrape()
        self.export_results()
        self.quit('Thank you for using ScraperAI!')

    def quit(self, message: str = None):
        if message:
            click.echo(message)
        if isinstance(self.crawler, SeleniumCrawler):
            self.crawler.driver.quit()
        exit(0)
