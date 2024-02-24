from abc import ABC, abstractmethod

import pandas as pd
from pydantic import BaseModel

from scraperai.parsing.classifier import WebpageType


class CatalogItem(BaseModel):
    card_classname: str
    url_classname: str
    html_snippet: str
    url: str


class BaseScraper(ABC):
    @property
    @abstractmethod
    def pagination_screenshot(self) -> bytes | None:
        ...

    @property
    @abstractmethod
    def total_spent(self) -> float:
        ...

    @property
    @abstractmethod
    def session_id(self) -> str:
        ...

    @property
    @abstractmethod
    def session_url(self) -> str:
        ...

    @property
    @abstractmethod
    def vnc_url(self) -> str | None:
        ...

    @abstractmethod
    def detect_page_type(self, url: str) -> WebpageType:
        ...

    @abstractmethod
    def detect_pagination(self, url: str) -> str | None:
        ...

    @abstractmethod
    def detect_catalog_item(self, url: str) -> CatalogItem | None:
        ...

    @abstractmethod
    def detect_details_on_card(self, html_snippet: str) -> dict[str, str]:
        ...

    @abstractmethod
    def detect_details_on_page(self, url: str) -> dict[str, str]:
        ...

    @abstractmethod
    def collect_data_from_catalog_pages(self,
                                        start_url: str,
                                        pagination_xpath: str,
                                        card_classname: str,
                                        selectors: dict[str, str]) -> pd.DataFrame:
        ...

    @abstractmethod
    def collect_urls_to_nested_pages(self, start_url: str, pagination_xpath: str, url_classname: str) -> list[str]:
        ...

    @abstractmethod
    def collect_nested_pages(self, urls: list[str], selectors: dict[str, str]) -> pd.DataFrame:
        ...
