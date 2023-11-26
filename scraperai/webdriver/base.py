from abc import abstractmethod, ABC


class BaseWebdriver(ABC):
    url: str

    def get(self, url: str):
        ...

    @abstractmethod
    def get_session_id(self) -> str:
        ...

    @property
    @abstractmethod
    def page_source(self) -> str:
        ...

    @abstractmethod
    def wait(self, timeout: float, locator):
        ...

    @abstractmethod
    def set_storage(self, key, value):
        ...

    @abstractmethod
    def execute_cdp_cmd(self, cmd: str, cmd_args: dict):
        ...

    @abstractmethod
    def quit(self):
        ...
