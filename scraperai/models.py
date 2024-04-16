import enum
from typing import Literal, Optional, Any
from pydantic import BaseModel


class StaticField(BaseModel):
    field_name: str
    field_xpath: str
    first_value: Optional[Any] = None


class DynamicField(BaseModel):
    section_name: str
    name_xpath: str
    value_xpath: str
    first_values: Optional[dict[str, str]] = None


class WebpageFields(BaseModel):
    static_fields: list[StaticField]
    dynamic_fields: list[DynamicField]

    @property
    def is_empty(self) -> bool:
        return len(self.static_fields) == 0 and len(self.dynamic_fields) == 0


class CatalogItem(BaseModel):
    card_xpath: str
    url_xpath: str
    html_snippet: str
    urls_on_page: list[str]

    def __repr__(self):
        urls_to_print = self.urls_on_page[0:3]
        if len(self.urls_on_page) > 3:
            urls_to_print.append(f'...')
        return f"""<card_xpath={self.card_xpath}
 url_xpath={self.url_xpath}
 urls_on_page={self.urls_on_page}
>"""


class Pagination(BaseModel):
    type: Literal['xpath', 'scroll', 'url_param']
    xpath: Optional[str] = None
    url_param: Optional[str] = None
    url_param_first_value: int = 1

    def __str__(self):
        if self.type == 'scroll':
            return f'Pagination using infinite scroll'
        elif self.type == 'xpath':
            return f'Pagination using button with xpath: {self.xpath}'
        else:
            return f'Pagination using url parameter "{self.url_param}"'


class WebpageType(str, enum.Enum):
    CATALOG = 'catalog'
    DETAILS = 'detailed_page'
    OTHER = 'other'
    CAPTCHA = 'captcha'

    @classmethod
    def values_repr(cls) -> str:
        return ', '.join([f'"{v}"' for v in cls])


class ScraperConfig(BaseModel):
    start_url: str
    page_type: Optional[WebpageType]
    pagination: Optional[Pagination]
    catalog_item: Optional[CatalogItem]
    open_nested_pages: bool
    fields: WebpageFields
    max_pages: int
    max_rows: int
