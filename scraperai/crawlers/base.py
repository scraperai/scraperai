from abc import ABC, abstractmethod


class BaseCrawler(ABC):
    @abstractmethod
    def get(self, url: str):
        ...

    @property
    @abstractmethod
    def page_source(self) -> str:
        ...

    @abstractmethod
    def click(self, xpath: str) -> None:
        ...

    @abstractmethod
    def get_screenshot_as_base64(self) -> str:
        raise NotImplementedError()
