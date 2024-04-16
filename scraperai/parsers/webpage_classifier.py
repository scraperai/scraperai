from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage

from scraperai.parsers.agent import ChatModelAgent
from scraperai.models import WebpageType
from scraperai.utils.image import encode_image_to_b64
from scraperai.lm.base import BaseVision, BaseJsonLM


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
            except ValueError:
                return f"{response} is not a valid page type. Should be one of {WebpageType.values_repr()}"
            return None

        messages = [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=[
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": encode_image_to_b64(screenshot)
                    },
                ]
            )
        ]

        text: str = self.query_with_validation(messages, _validate_response, max_retries=2)
        return WebpageType(text)


class WebpageTextClassifier:
    def __init__(self, model: BaseJsonLM):
        self.model = model

    def classify(self, html_content: str) -> WebpageType:
        # TODO: Add prompt
        messages = [
            SystemMessage(
                content="Your goal is to classify webpages by screenshot."
            ),
            HumanMessage(
                content=""
            ),
        ]
        response = self.model.invoke(messages)
        return WebpageType(response)
