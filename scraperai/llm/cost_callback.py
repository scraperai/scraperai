import logging
import threading
from contextlib import contextmanager
from typing import Any, Generator

import tiktoken
from langchain_community.callbacks.manager import openai_callback_var
from langchain_community.callbacks.openai_info import (
    standardize_model_name,
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
    OpenAICallbackHandler
)
from langchain_core.outputs import LLMResult


logger = logging.getLogger(__name__)


class CostTrackerCallback(OpenAICallbackHandler):
    """Callback handler to track the cost of the model."""

    def __init__(self) -> None:
        super().__init__()
        self.model_name: str = ''
        # NOTE: Using this way to calculate the token is just a rough estimate,
        # as the functions sent to the API is not counted. We have to wait for Langchain to fix it.
        self.encoding = tiktoken.get_encoding("cl100k_base")
        self._lock = threading.Lock()

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        **kwargs: Any,
    ) -> None:
        """Calculates the prompt token number and cost."""
        prompts_string = ''.join(prompts)
        prompt_tokens = len(self.encoding.encode(prompts_string))
        model_name = serialized.get('kwargs', dict()).get('model_name', '')
        self.model_name = standardize_model_name(model_name)
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(self.model_name, prompt_tokens)
        else:
            logger.warning(f"Model name {self.model_name} not found. Cannot calculate cost.")
            prompt_cost = 0

        with self._lock:
            self.prompt_tokens += prompt_tokens
            self.total_tokens += prompt_tokens
            self.total_cost += prompt_cost

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Calculates the completion token number and cost."""
        text_response = response.generations[0][0].text
        completion_tokens = len(self.encoding.encode(text_response))
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            completion_cost = get_openai_token_cost_for_model(
                self.model_name, completion_tokens, is_completion=True
            )
        else:
            logger.warning(f"Model {self.model_name} not found in cost per 1k tokens.")
            completion_cost = 0

        # update shared state behind lock in case async runs.
        with self._lock:
            self.total_cost += completion_cost
            self.total_tokens += completion_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1


@contextmanager
def get_cost_tracker_callback() -> Generator[CostTrackerCallback, None, None]:
    cb = CostTrackerCallback()
    openai_callback_var.set(cb)
    yield cb
    openai_callback_var.set(None)
