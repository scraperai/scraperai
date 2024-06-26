from __future__ import annotations

import enum
from typing import Literal, Optional, Any
import uuid

import pydantic
from pydantic import BaseModel


class StaticField(BaseModel):
    field_name: str
    field_xpath: str
    first_value: Optional[Any] = None
    multiple: bool = False
    extract_mode: Literal['text', 'href', 'src'] = 'text'
    id: uuid.UUID = uuid.uuid4()
    color: Optional[str] = None


class DynamicField(BaseModel):
    section_name: str
    name_xpath: str
    value_xpath: str
    first_values: Optional[dict[str, str]] = None
    id: uuid.UUID = uuid.uuid4()
    color: Optional[str] = None


class WebpageFields(BaseModel):
    static_fields: list[StaticField]
    dynamic_fields: list[DynamicField]

    @property
    def is_empty(self) -> bool:
        return len(self.static_fields) == 0 and len(self.dynamic_fields) == 0


class CatalogItem(BaseModel):
    card_xpath: str
    url_xpath: Optional[str]
    html_snippet: str = pydantic.Field(..., repr=False)
    urls_on_page: list[str]


class Pagination(BaseModel):
    type: Literal['xpath', 'scroll', 'urls', 'none']
    xpath: Optional[str] = None
    urls: list[str] = pydantic.Field([], repr=False)

    def __str__(self):
        match self.type:
            case 'scroll':
                return f'Pagination using infinite scroll'
            case 'xpath':
                return f'Pagination using button with xpath: {self.xpath}'
            case 'urls':
                return f'Pagination with list of urls (total of {len(self.urls)})'
            case _:
                return 'No pagination'


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
    pagination: Pagination
    catalog_item: Optional[CatalogItem]
    open_nested_pages: bool
    fields: WebpageFields
    max_pages: int
    max_rows: int
