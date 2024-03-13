import datetime
import json
import os
from typing import Literal

import click
import pandas as pd
from dotenv import find_dotenv, load_dotenv

from scraperai.parsers import WebpageType, Pagination
from scraperai.parsers.models import CatalogItem, WebpageFields
from scraperai.scraper import ScraperAI
from scraperai.crawlers import SeleniumCrawler


class App:
    page_type: WebpageType = None
    pagination: Pagination = None
    catalog_item: CatalogItem = None
    fields: WebpageFields = None
    open_nested_pages: bool = False
    max_pages: int = 1
    max_rows: int = 1
    output_format: Literal['json', 'xlsx', 'csv'] = 'json'
    rows: list = []

    def __init__(self, openai_api_key: str, start_url: str):
        self.start_url = start_url
        click.echo('Starting webdriver...')
        self.crawler = SeleniumCrawler()
        click.echo(f'Webdriver is ok')
        self.scraper = ScraperAI(crawler=self.crawler, openai_api_key=openai_api_key)

    def detect_page_type(self) -> WebpageType:
        click.echo(f'Detecting page type...')
        page_type = self.scraper.detect_page_type(self.start_url)
        click.echo(f'Detected page type: {page_type.value}')

        if click.confirm('Do you want to change it?', default=False):
            types = [opt.value for opt in [WebpageType.CATALOG, WebpageType.DETAILS, WebpageType.OTHER]]
            new_type = click.prompt(
                f'Enter page type',
                type=click.Choice(types, case_sensitive=False)
            )
            page_type = WebpageType(new_type)
        self.page_type = page_type
        return page_type

    def detect_pagination(self) -> Pagination:
        click.echo(f'Detecting pagination...')
        pagination = self.scraper.detect_pagination(self.start_url)
        click.echo(f'Detected pagination: {pagination}')
        if click.confirm('Do you want to change it?', default=False):
            types = ['xpath', 'scroll', 'url_param']
            new_type = click.prompt(
                f'Enter pagination type',
                type=click.Choice(types, case_sensitive=False)
            )
            new_xpath = None
            new_url_param = None
            if new_type == 'xpath':
                new_xpath = click.prompt(f'Enter next-page button xpath')
            elif new_type == 'url_param':
                new_url_param = click.prompt(f'Enter page url param name')
            pagination = Pagination(
                type=new_type,
                xpath=new_xpath,
                url_param=new_url_param
            )

        self.pagination = pagination
        return pagination

    def detect_catalog_item(self, extra_prompt: str = None, catalog_item: CatalogItem = None) -> CatalogItem:
        click.echo(f'Detecting catalog item...')
        if catalog_item is None:
            catalog_item = self.scraper.detect_catalog_item(self.start_url, extra_prompt)
        if catalog_item:
            urls_to_print = catalog_item.urls_on_page[0:3]
            if len(catalog_item.urls_on_page) > 3:
                urls_to_print.append('...')

            urls_text = '\n'.join(['  - ' + u for u in urls_to_print])
            click.echo(f'Detected catalog item!\n'
                       f'- card xpath: {catalog_item.card_xpath}\n'
                       f'- href xpath: {catalog_item.url_xpath}\n'
                       f'- urls on page ({len(catalog_item.urls_on_page)}):\n'
                       f'{urls_text}')
        else:
            click.echo('Could not find catalog_item')
        if click.confirm('Do you want to change it?', default=False):
            if click.confirm("Do you know card's xpath?", default=False):
                new_card_xpath = click.prompt('Enter xpath to select catalog cards')
                new_url_xpath = click.prompt('Enter xpath to select urls to nested pages')
                catalog_item = self.scraper.manually_change_catalog_item(self.start_url, new_card_xpath, new_url_xpath)
                return self.detect_catalog_item(catalog_item=catalog_item)
            else:
                user_suggestion = click.prompt('Enter description of the card')
                extra_prompt = f'You have made a mistake.' \
                               f'{catalog_item.card_xpath} is not a correct xpath of catalog card. ' \
                               f'I can give you following instruction: {user_suggestion}'
                return self.detect_catalog_item(extra_prompt)

        if catalog_item is None:
            self.quit('Could not find catalog item. Aborting...')
        self.catalog_item = catalog_item
        return catalog_item

    def ask_if_open_nested_pages(self) -> bool:
        self.open_nested_pages = click.confirm('Do you want to parse nested pages?', default=True)
        return self.open_nested_pages

    @staticmethod
    def _print_fields(fields: WebpageFields):
        click.echo(f'Static fields ({len(fields.static_fields)}):')

        data = [{'name': f.field_name, 'xpath': f.field_xpath, 'value': f.first_value} for f in fields.static_fields]
        df = pd.DataFrame(data)
        click.echo(df.to_markdown(tablefmt='plain', index=True))

        click.echo('')
        click.echo(f'Dynamic fields ({len(fields.dynamic_fields)}):')
        if len(fields.dynamic_fields) == 0:
            click.echo('Not found')
            return
        index = len(fields.static_fields)
        for field in fields.dynamic_fields:
            click.echo(f' {index}  Section {field.section_name}\n'
                       f'    Labels xpath: {field.name_xpath}\n'
                       f'    Values xpath: {field.value_xpath}\n'
                       f'    Value: {field.first_values}')
            index += 1

    def detect_fields(self, *, nested_page_url: str = None, html_snippet: str = None) -> WebpageFields:

        if nested_page_url is not None:
            click.echo(f'Loading nested page and detecting data fields...')
            html_snippet = self.scraper.summarize_details_page_as_valid_html(nested_page_url)
            fields = self.scraper.extract_fields(html_snippet)
        elif html_snippet is not None:
            click.echo(f'Detecting data fields...')
            fields = self.scraper.extract_fields(html_snippet)
        else:
            raise ValueError

        self._print_fields(fields)
        while True:
            if not click.confirm('Do you want to edit fields?', default=False):
                break

            action_type = click.prompt('Do you want to remove or add field?',
                                       type=click.Choice(['add', 'remove'], case_sensitive=False))
            if action_type == 'add':
                user_description = click.prompt('Enter description of the field(s)')
                click.echo('Searching...')
                new_fields = self.scraper.find_fields(html_snippet, user_description)
                if new_fields.is_empty:
                    click.echo(f'Nothing found:(')
                else:
                    fields.static_fields += new_fields.static_fields
                    fields.dynamic_fields += new_fields.dynamic_fields
                    self._print_fields(fields)
            else:
                field_name = click.prompt('Enter field name or index')
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
                    self._print_fields(fields)
                else:
                    click.echo('No such field')
        click.echo('Detection finished!')
        self.fields = fields
        return fields

    def ask_for_max_pages_and_items(self):
        self.max_pages = click.prompt('Enter catalog pages limit', type=int, default=3)
        self.max_rows = click.prompt('Enter rows limit', type=int, default=50)

    def show_scraping_formula(self):
        if self.catalog_item:
            catalog_item = f'(card_xpath={self.catalog_item.card_xpath}, url_xpath={self.catalog_item.url_xpath})'
        else:
            catalog_item = "-"
        click.echo(f'\n'
                   f'Parsing summary:\n'
                   f' - Start url: {self.start_url}'
                   f' - Start page type: {self.page_type}\n'
                   f' - Pagination: {self.pagination or "-"}\n'
                   f' - Catalog item: {catalog_item}\n'
                   f' - Open nested pages: {self.open_nested_pages}\n'
                   f' - Fields: {len(self.fields.static_fields)} static, {len(self.fields.dynamic_fields)} dynamic\n'
                   f' - Max pages: {self.max_pages}\n'
                   f' - Max rows: {self.max_rows}\n'
                   f' - Total OpenAI cost, $: {self.scraper.total_cost:.3f}\n')
        click.confirm('Press enter to start scraping', default=True)

    def scrape(self):
        click.echo('Starting scraping...')
        if self.page_type == WebpageType.OTHER:
            self.quit('Unsupported page type. Aborting...')
            return
        elif self.page_type == WebpageType.DETAILS:
            rows = self.scraper.collect_data_from_nested_pages([self.start_url], self.fields)
        else:
            if self.open_nested_pages:
                urls = self.scraper.collect_urls_to_nested_pages(
                    self.start_url,
                    self.pagination,
                    self.catalog_item.url_xpath,
                    self.max_pages
                )
                click.echo(f'Collected {len(urls)} urls to nested pages')
                urls = urls[:self.max_rows]
                click.echo(f'Start collecting data from {len(urls)} nested pages')
                rows = self.scraper.collect_data_from_nested_pages(urls, self.fields)
            else:
                rows = self.scraper.collect_data_from_catalog_pages(
                    self.start_url,
                    self.pagination,
                    self.catalog_item.card_xpath,
                    self.fields,
                    self.max_pages,
                    self.max_rows
                )

        click.echo(f'Successfully collected {len(rows)} rows. Exporting results...')
        self.rows = rows

    def export_results(self):
        while True:
            types = ['json', 'xlsx', 'csv']
            self.output_format = click.prompt('Choose output format',
                                              type=click.Choice(types, case_sensitive=False),
                                              default='json')

            rows = self.rows
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'results_{timestamp}.{self.output_format}'
            if self.output_format == 'json':
                with open(filename, 'w+') as f:
                    json.dump(rows, f, indent=4, ensure_ascii=False)
            elif self.output_format == 'xlsx':
                df = pd.DataFrame(rows)
                df.to_excel(filename)
            elif self.output_format == 'csv':
                df = pd.DataFrame(rows)
                df.to_csv(filename)
            click.echo(f'Exported results to {filename}')
            if not click.confirm(f'Do you want to export in other format?', default=False):
                break
        click.echo('Thank you for using ScraperAI!')

    def run(self):
        # Step 3: Detect page type
        page_type = self.detect_page_type()

        if page_type == WebpageType.OTHER:
            self.quit('Unsupported page type. Aborting...')
        elif page_type == WebpageType.CATALOG:
            # Step 4: Detect pagination
            self.detect_pagination()
            # Step 5: Detect catalog item
            catalog_item = self.detect_catalog_item()
            # Step 6: Detect fields
            open_nested_pages = self.ask_if_open_nested_pages()
            if open_nested_pages:
                self.detect_fields(nested_page_url=catalog_item.urls_on_page[0])
            else:
                self.detect_fields(html_snippet=catalog_item.html_snippet)
            self.ask_for_max_pages_and_items()
        elif page_type == WebpageType.DETAILS:
            self.detect_fields(nested_page_url=self.start_url)

        # Step 8: Scraping all pages accroding to the task
        self.show_scraping_formula()
        self.scrape()
        self.export_results()

    def quit(self, message: str = None):
        if message:
            click.echo(message)
        self.crawler.driver.quit()
        exit(0)


@click.command()
@click.option('--url', prompt='Enter url', help='url of the catalog or product page of any website')
def main(url: str):
    """ScraperAI CLI Application
    
    You need openai api key to use this application. There are two ways to pass the key. 
    The first is to add OPENAI_API_KEY to your environment or create .env file.
    Second option is to pass api key to the script (you will be asked).
    """

    # Step 1: Get openai token
    env_file = find_dotenv()
    if env_file:
        load_dotenv()
    openai_api_key = os.getenv('OPENAI_API_KEY')
    if openai_api_key is None:
        click.echo('OPENAI_API_KEY was not found in .env')
    if openai_api_key is None:
        openai_api_key = click.prompt('Enter your openai token')

    # Step 2: Init crawler and scraper
    app = App(openai_api_key, url)
    try:
        app.run()
    except Exception as e:
        click.echo(f'Unexpected exception: {e}')
        raise e
    app.quit()


if __name__ == '__main__':
    main()
