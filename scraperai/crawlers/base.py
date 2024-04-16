import logging
from abc import ABC, abstractmethod

from scraperai.models import Pagination

logger = logging.getLogger(__file__)


class BaseCrawler(ABC):
    @abstractmethod
    def get(self, url: str):
        ...

    @property
    @abstractmethod
    def page_source(self) -> str:
        ...

    @abstractmethod
    def switch_page(self, pagination: Pagination) -> bool:
        raise NotImplementedError()
