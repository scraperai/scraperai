from abc import ABC, abstractmethod
from pathlib import Path


class BaseVision(ABC):
    @abstractmethod
    def invoke(self,
               user_prompt: str,
               system_prompt: str,
               image: bytes | str | Path) -> str:
        ...
