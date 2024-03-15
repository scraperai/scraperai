from abc import ABC, abstractmethod
from typing import Union, Dict, Any, Type, TypeVar, List

from pydantic import BaseModel

_BM = TypeVar("_BM", bound=BaseModel)
_DictOrList = Dict[str, Any] | List[Any]
_DictOrPydanticClass = Union[_DictOrList, Type[_BM]]


class BaseLM(ABC):
    @abstractmethod
    def invoke(self, user_prompt: str, system_prompt: str, **kwargs) -> str:
        ...


class BaseJsonLM(ABC):
    @abstractmethod
    def invoke(self, user_prompt: str, system_prompt: str, **kwargs) -> _DictOrList:
        ...
