from typing import Literal, Optional, Any
from pydantic import BaseModel


class StaticField(BaseModel):
    field_name: str
    field_xpath: str
    field_type: Literal['single', 'array'] = 'single'
    iterator_xpath: Optional[str] = None
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
