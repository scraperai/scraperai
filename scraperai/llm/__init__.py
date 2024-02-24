import time
import logging

from pathlib import Path
from openai import OpenAI, RateLimitError
from retry import retry

from .models import ChatModelResponse, OpenAIModelPrices, OpenAIModel


# Suppress openai logging
logging.getLogger('openai').setLevel(logging.WARNING)
logging.getLogger('httpx').setLevel(logging.WARNING)
logger = logging.getLogger(__file__)


class OpenAIChatModel:
    def __init__(self, api_key: str, model: OpenAIModel = OpenAIModel.gpt4):
        self.client = OpenAI(api_key=api_key)
        self.model = model

    @retry(RateLimitError, tries=5, delay=5, backoff=1.5, max_delay=15)
    def get_answer(self,
                   user_prompt: str,
                   system_prompt: str = None,
                   image: bytes | str | Path = None,
                   max_tokens: int | None = None,
                   force_json: bool = False) -> ChatModelResponse:

        start = time.time()
        # Build message
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        if image:
            from ..utils.image import encode_image_to_b64

            messages.append({
                'role': 'user',
                'content': [
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": encode_image_to_b64(image),
                    },
                ]
            })
        else:
            messages.append({'role': 'user', 'content': user_prompt})

        kwargs = {
            'model': self.model.value,
            'messages': messages,
            'max_tokens': max_tokens,
        }
        if force_json and not image:
            kwargs['response_format'] = {'type': 'json_object'}

        # Fetch response
        resp = self.client.chat.completions.create(**kwargs)
        content = resp.choices[0].message.content

        in_price, out_price = OpenAIModelPrices[self.model][0], OpenAIModelPrices[self.model][1]
        price = (in_price * resp.usage.prompt_tokens + out_price * resp.usage.completion_tokens) / 1000.0

        logger.info(f'OpenAIChatModel: spent {price:.3f} USD, took {time.time() - start:.2f} seconds')
        return ChatModelResponse(text=content, price=price)
