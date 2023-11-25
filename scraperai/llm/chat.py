import enum

import openai
from retry import retry

import settings
from .base import ChatModel


class OpenAIModel(enum.Enum):
    gpt4 = 'gpt-4'
    gpt3 = 'gpt-3.5-turbo'
    gpt3_large = 'gpt-3.5-turbo-16k'


class OpenAIChatModel(ChatModel):
    def __init__(self, model: OpenAIModel = OpenAIModel.gpt4):
        openai.api_key = settings.OPEN_AI_TOKEN
        self.model = model

    @retry(openai.error.RateLimitError, tries=5, delay=5, backoff=1.5, max_delay=15)
    def get_answer(self, user_prompt: str, system_prompt: str, max_tokens: int | None = None):
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_prompt}
        ]
        resp = openai.ChatCompletion.create(
            model=self.model.value,
            messages=messages,
            temperature=0.1,
            max_tokens=max_tokens,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
        )
        return resp.choices[0].message.content
