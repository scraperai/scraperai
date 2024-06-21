from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Type, TypeVar

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

_BM = TypeVar("_BM", bound=BaseModel)
_Dict = Dict[str, Any]
_DictOrPydanticClass = Union[_Dict, Type[_BM]]


class BaseJsonLM(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> _Dict:
        ...


class BaseVision(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> str:
        ...
