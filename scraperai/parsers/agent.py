import logging
from typing import Callable, Any, Optional

from langchain_core.messages import BaseMessage, HumanMessage

from scraperai.lm import BaseLM, BaseJsonLM, BaseVision


logger = logging.getLogger(__file__)


class ChatModelAgent:
    def __init__(self, model: BaseLM | BaseJsonLM | BaseVision):
        self.model = model

    def query_with_validation(self,
                              messages: list[BaseMessage],
                              validator: Callable[[Any], Optional[str]],
                              max_retries: int = 3,
                              current_try: int = 0) -> Any:
        response = self.model.invoke(messages)
        new_error_message = validator(response)
        if new_error_message is None:
            return response

        logger.warning(f'Got error message: {new_error_message}')
        if current_try < max_retries:
            messages.append(HumanMessage(content=new_error_message))
            return self.query_with_validation(messages, validator, max_retries, current_try + 1)
        else:
            raise Exception(new_error_message)
