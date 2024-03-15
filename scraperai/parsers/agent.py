import logging
from typing import Callable, Any, Optional

from scraperai.lm import BaseLM, BaseJsonLM
from scraperai.vision import BaseVision


logger = logging.getLogger(__file__)


class ChatModelAgent:
    def __init__(self, model: BaseLM | BaseJsonLM | BaseVision):
        self.model = model

    def query_with_validation(self,
                              prompt: str,
                              system_prompt: str,
                              validator: Callable[[Any], Optional[str]],
                              error_message: str = None,
                              max_retries: int = 3,
                              current_try: int = 1) -> Any:
        if error_message:
            system_prompt = f"{system_prompt}\nNote: {error_message}"

        response = self.model.invoke(prompt, system_prompt)
        new_error_message = validator(response)
        if new_error_message is None:
            return response

        logger.warning(f'Got error message: {new_error_message}')
        if current_try < max_retries:
            return self.query_with_validation(prompt,
                                              system_prompt,
                                              validator,
                                              new_error_message,
                                              max_retries,
                                              current_try + 1)
        else:
            raise Exception(new_error_message)
