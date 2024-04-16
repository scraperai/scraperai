from typing import Literal

import click
import pandas as pd

from scraperai.cli.model import ScreenStatus, CardEditFormModel, FieldsEditFormModel
from scraperai.models import CatalogItem, WebpageFields, WebpageType, Pagination, ScraperConfig


class View:
    progressbar = click.progressbar

    def show_configs_search_screen(self, config: ScraperConfig) -> bool:
        click.echo(f'Found stored config for start_url={config.start_url}')
        self.show_config_screen(config, show_limits=False)
        return click.confirm(f'Do you want to use it?', default=True)
    
    def show_api_key_screen(self, status: ScreenStatus) -> tuple[str, bool] | None:
        if status == ScreenStatus.loading:
            click.echo('Searching for openai api key')
        elif status == ScreenStatus.show:
            click.echo('Successfully found openai api key')
        elif status == ScreenStatus.edit:
            click.echo('OPENAI_API_KEY was not found in environment')
            api_key = click.prompt('Enter your openai api key')
            should_save = click.confirm('Do you want to save key in local .env?', default=True)
            return api_key, should_save

    def show_page_type_screen(self, status: ScreenStatus, page_type: WebpageType = None) -> WebpageType | None:
        if status == ScreenStatus.loading:
            click.echo('Detecting page type...')
        elif status == ScreenStatus.show:
            click.echo(f'Detected page type: {page_type.value}')
        elif status == ScreenStatus.edit:
            if click.confirm('Do you want to change page type?', default=False):
                types = [opt.value for opt in [WebpageType.CATALOG, WebpageType.DETAILS, WebpageType.OTHER]]
                new_type = click.prompt(
                    f'Enter page type',
                    type=click.Choice(types, case_sensitive=False)
                )
                page_type = WebpageType(new_type)
        return page_type

    def show_captcha_warning(self) -> bool:
        click.echo('Captcha detected! Please solve it before we can continue')
        return click.confirm('Do you wish to retry?', default=True)

    def show_pagination_screen(self,
                               status: ScreenStatus,
                               pagination: Pagination = None) -> Pagination | None:
        if status == ScreenStatus.loading:
            click.echo(f'Detecting pagination...')
        elif status == ScreenStatus.show:
            click.echo(f'Detected pagination: {pagination}')
        elif status == ScreenStatus.edit:
            if click.confirm('Do you want to change pagination?', default=False):
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
        return pagination

    def show_card_screen(self, status: ScreenStatus, catalog_item: CatalogItem = None) -> CardEditFormModel | None:
        if status == ScreenStatus.loading:
            click.echo(f'Detecting catalog item...')

        elif status == ScreenStatus.show:
            if catalog_item is None:
                click.echo('Could not find catalog_item')
            else:
                urls_to_print = catalog_item.urls_on_page[0:3]
                if len(catalog_item.urls_on_page) > 3:
                    urls_to_print.append('...')

                urls_text = '\n'.join(['  - ' + u for u in urls_to_print])
                click.echo(f'Detected catalog item!\n'
                           f'- card xpath: {catalog_item.card_xpath}\n'
                           f'- href xpath: {catalog_item.url_xpath}\n'
                           f'- urls on page ({len(catalog_item.urls_on_page)}+):\n'
                           f'{urls_text}')

        elif status == ScreenStatus.edit:
            model = CardEditFormModel(has_changes=False)
            if click.confirm('Do you want to change it?', default=catalog_item is None):
                model.has_changes = True
                if click.confirm("Do you know card's xpath?", default=False):
                    model.new_card_xpath = click.prompt('Enter xpath to select catalog cards')
                    model.new_url_xpath = click.prompt('Enter xpath to select urls to nested pages')
                else:
                    model.user_suggestion = click.prompt('Enter description of the card')
            return model

    def show_open_nested_pages_screen(self) -> bool:
        return click.confirm('Do you want to parse nested pages?', default=False)

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

    def show_fields_screen(self,
                           status: ScreenStatus,
                           fields: WebpageFields = None,
                           not_found_message: str = None) -> FieldsEditFormModel | None:
        if status == ScreenStatus.loading:
            click.echo('Detecting data fields...')
        elif status == ScreenStatus.show:
            if not_found_message:
                click.echo(not_found_message)
            else:
                self._print_fields(fields)
        elif status == ScreenStatus.edit:
            model = FieldsEditFormModel(has_changes=False)
            if click.confirm('Do you want to edit fields?', default=False):
                model.has_changes = True
                model.action_type = click.prompt(
                    'Do you want to add or remove field?',
                    type=click.Choice(['a', 'r'], case_sensitive=False),
                    default='a'
                )
                if model.action_type == 'a':
                    model.user_suggestion = click.prompt('Enter description of the field(s)')
                else:
                    model.field_to_delete = click.prompt('Enter field name, index or range (e.g. 1-3,5,6)')
            return model

    def show_limits_screen(self) -> tuple[int, int]:
        max_pages = click.prompt('Enter catalog pages limit', type=int, default=3)
        max_rows = click.prompt('Enter rows limit', type=int, default=50)
        return max_pages, max_rows

    def show_config_screen(self, config: ScraperConfig,
                           total_cost: float = None,
                           show_limits: bool = True) -> None:
        if config.catalog_item:
            catalog_item = f'(card_xpath={config.catalog_item.card_xpath}, url_xpath={config.catalog_item.url_xpath})'
        else:
            catalog_item = '-'
        text = f'Scraper Config:\n'
        text += f' - Start url: {config.start_url}\n'
        text += f' - Start page type: {config.page_type}\n'
        text += f' - Pagination: {config.pagination or "-"}\n'
        text += f' - Catalog item: {catalog_item}\n'
        text += f' - Open nested pages: {config.open_nested_pages}\n'
        text += f' - Fields: {len(config.fields.static_fields)} static, {len(config.fields.dynamic_fields)} dynamic\n'
        if show_limits:
            text += f' - Max pages: {config.max_pages}\n'
            text += f' - Max rows: {config.max_rows}\n'
        if total_cost:
            text += f' - Total OpenAI cost, $: {total_cost:.3f}\n'
        click.echo(text)

    def show_config_save_screen(self) -> bool:
        return click.confirm('Do you want to save config to reuse in future?', default=True)

    def show_export_screen(self,
                           status: ScreenStatus,
                           data_size: int = None,
                           force_yes: bool = True,
                           filename: str = None) -> Literal['json', 'xlsx', 'csv'] | None:
        if status == ScreenStatus.loading:
            click.echo(f'Successfully collected {data_size} rows. Preparing data for export...')
        elif status == ScreenStatus.show:
            if filename:
                click.echo(f'Exported results to {filename}')
            else:
                click.echo('Ready to export data')
        else:
            if not force_yes:
                if not click.confirm(f'Do you want to export in other format?', default=False):
                    return None
            types = ['json', 'xlsx', 'csv']
            return click.prompt('Choose output format',
                                type=click.Choice(types, case_sensitive=False),
                                default='json')
