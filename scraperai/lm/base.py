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
    def invoke(self, user_prompt: str, system_prompt: str, **kwargs) -> _DictOrPydanticClass:
        ...

    def invoke_as_json(self, user_prompt: str, system_prompt: str, **kwargs) -> _DictOrList:
        response = self.invoke(user_prompt, system_prompt, **kwargs)
        if isinstance(response, BaseModel):
            return response.model_dump()
        elif isinstance(response, dict):
            return response
        elif isinstance(response, list):
            return response
        else:
            raise TypeError(f'Invalid response type: {type(response)}')
