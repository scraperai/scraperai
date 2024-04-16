import json
import logging
from typing import Optional

from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
from pydantic import BaseModel

from scraperai.lm.base import BaseLM, BaseJsonLM, _Dict, _DictOrPydanticClass, BaseVision

logger = logging.getLogger('scraperai')


class OpenAI(BaseLM):
    latest = 'gpt-4-0125-preview'

    def __init__(self,
                 openai_api_key: str,
                 openai_organization: str = None,
                 model_name: str = latest,
                 **kwargs):
        self.chat = ChatOpenAI(model=model_name,
                               openai_api_key=openai_api_key,
                               openai_organization=openai_organization,
                               max_retries=3,
                               **kwargs)
        self.total_cost = 0

    def invoke(self, messages: list[BaseMessage]) -> str:
        with get_openai_callback() as cb:
            r = self.chat.invoke(messages).content
            self.total_cost += cb.total_cost
            logger.info(f"Total Tokens: {cb.total_tokens}, Total Cost (USD): ${cb.total_cost:.3f}")
        r = r.strip('```').strip('\n').strip()
        return r


class JsonOpenAI(BaseJsonLM):
    latest = 'gpt-4-0125-preview'

    def __init__(self,
                 openai_api_key: str,
                 openai_organization: str = None,
                 model_name: str = latest,
                 schema: Optional[_DictOrPydanticClass] = None,
                 **kwargs):
        model_kwargs = {"response_format": {"type": "json_object"}}
        self.chat = ChatOpenAI(model=model_name,
                               model_kwargs=model_kwargs,
                               openai_api_key=openai_api_key,
                               openai_organization=openai_organization,
                               max_retries=3,
                               **kwargs)
        self.model_with_structure = None
        if schema:
            self.model_with_structure = self.chat.with_structured_output(schema, method='json_mode')
        self.total_cost = 0

    def invoke(self, messages: list[BaseMessage]) -> _Dict:
        with get_openai_callback() as cb:
            if self.model_with_structure:
                response = self.model_with_structure.invoke(messages)
            else:
                text = self.chat.invoke(messages).content
                response = json.loads(text)
            self.total_cost += cb.total_cost
            logger.info(f"Total Tokens: {cb.total_tokens}, Total Cost (USD): ${cb.total_cost:.3f}")

        if isinstance(response, BaseModel):
            return response.model_dump()
        else:
            return response


class VisionOpenAI(BaseVision):
    latest = 'gpt-4-vision-preview'

    def __init__(self,
                 openai_api_key: str,
                 openai_organization: str = None,
                 model_name: str = latest,
                 **kwargs):
        self.total_cost = 0.0
        self.chat = ChatOpenAI(model=model_name,
                               openai_api_key=openai_api_key,
                               openai_organization=openai_organization,
                               **kwargs)

    def invoke(self, messages: list[BaseMessage]) -> str:
        with get_openai_callback() as cb:
            response = self.chat.invoke(messages).content
            self.total_cost += cb.total_cost
        return response
