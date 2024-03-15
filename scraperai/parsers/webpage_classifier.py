import enum
from typing import Optional

from scraperai.parsers.agent import ChatModelAgent
from scraperai.vision.base import BaseVision
from scraperai.lm.base import BaseLM


class WebpageType(str, enum.Enum):
    CATALOG = 'catalog'
    DETAILS = 'detailed_page'
    OTHER = 'other'
    CAPTCHA = 'captcha'

    @classmethod
    def values_repr(cls) -> str:
        return ', '.join([f'"{v.value}"' for v in cls])


class WebpageVisionClassifier(ChatModelAgent):
    def __init__(self, model: BaseVision):
        super().__init__(model)
        self.model = model

    def classify(self, screenshot: str) -> WebpageType:
        system_prompt = f"""
Your goal is to classify website by screenshot into 4 categories - {WebpageType.values_repr()}.
"catalog" page contains a table or a list of similar elements or cards.
"detailed_page" contains description of one product.
In other cases return "other".
Return only category name in the answer.
"""
        user_prompt = ""

        def _validate_response(response: str) -> Optional[str]:
            try:
                WebpageType(response)
            except ValueError as e:
                return f"{response} is not a valid page type. Should be one of {WebpageType.values_repr()}"
        text: str = self.query_with_validation(user_prompt, system_prompt, _validate_response, max_retries=2)
        return WebpageType(text)


class WebpageTextClassifier:
    def __init__(self, model: BaseLM):
        self.model = model

    def classify(self, html: str) -> WebpageType:
        system_prompt = "Your goal is to classify webpages by screenshot."
        # TODO: Add prompt
        user_prompt = """

"""
        response = self.model.invoke(user_prompt, system_prompt)
        return WebpageType(response)
