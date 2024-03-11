from typing import Literal, Optional
from pydantic import BaseModel


class StaticField(BaseModel):
    field_name: str
    field_xpath: str
    field_type: Literal['single', 'array'] = 'single'
    iterator_xpath: Optional[str] = None


class DynamicField(BaseModel):
    section_name: str
    name_xpath: str
    value_xpath: str


class WebpageFields(BaseModel):
    static_fields: list[StaticField]
    dynamic_fields: list[DynamicField]


class CatalogItem(BaseModel):
    card_classname: str
    url_classname: str
    html_snippet: str
    url: str
