from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Type, TypeVar, List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel

_BM = TypeVar("_BM", bound=BaseModel)
_DictOrList = Dict[str, Any] | List[Any]
_DictOrPydanticClass = Union[_DictOrList, Type[_BM]]


class BaseLM(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> str:
        ...


class BaseJsonLM(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> _DictOrList:
        ...


class BaseVision(ABC):
    @abstractmethod
    def invoke(self, messages: list[BaseMessage]) -> str:
        ...
