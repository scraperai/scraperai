import logging
from typing import Callable, Any, Optional

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from scraperai.lm import BaseJsonLM, BaseVision


logger = logging.getLogger('scraperai')


class ChatModelAgent:
    def __init__(self, model: BaseJsonLM | BaseVision):
        self.model = model

    def query_with_validation(self,
                              messages: list[BaseMessage],
                              validator: Callable[[Any], Optional[str]],
                              max_retries: int = 3,
                              current_try: int = 0) -> Any:
        response = self.model.invoke(messages)
        logger.debug(f'Got response: {response}')
        try:
            new_error_message = validator(response)
        except Exception:
            new_error_message = None
        if new_error_message is None:
            return response

        logger.warning(f'Validation failed with message: {new_error_message}')
        if current_try < max_retries:
            new_messages = messages + [
                AIMessage(content=str(response)),
                HumanMessage(content='Your previous response was wrong because ' + new_error_message)
            ]
            print(len(new_messages))
            return self.query_with_validation(new_messages, validator, max_retries, current_try + 1)
        else:
            raise Exception(new_error_message)
