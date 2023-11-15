from abc import ABC


class ChatModel(ABC):
    def get_answer(self, user_prompt: str, system_prompt: str, max_tokens: int | None = None):
        ...
