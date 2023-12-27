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
    def wait(self, timeout: float, locator) -> None:
        ...

    @abstractmethod
    def set_storage(self, key, value) -> None:
        ...

    @abstractmethod
    def execute_cdp_cmd(self, cmd: str, cmd_args: dict) -> None:
        ...

    @abstractmethod
    def execute_script(self, script, *args) -> None:
        ...

    @abstractmethod
    def get_screenshot_as_base64(self) -> str:
        ...

    @abstractmethod
    def quit(self) -> None:
        ...
