from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import TokenTextSplitter

from scraperai.parsers.agent import ChatModelAgent
from scraperai.models import WebpageType
from scraperai.utils.html import minify_html
from scraperai.utils.image import encode_image_to_b64
from scraperai.llm.base import BaseVision, BaseJsonLM


class WebpageVisionClassifier(ChatModelAgent):
    def __init__(self, model: BaseVision):
        super().__init__(model)
        self.model = model

    def classify(self, screenshot: str) -> WebpageType:
        system_prompt = f"""
Your goal is to classify website by screenshot into 2 categories - "catalog", "detailed_page".
"catalog" page contains a table or a list of similar elements or cards.
"detailed_page" contains description of one product.
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
                        "image_url": {
                            "url": encode_image_to_b64(screenshot)
                        }
                    },
                ]
            )
        ]

        text: str = self.query_with_validation(messages, _validate_response, max_retries=2)
        return WebpageType(text)


class WebpageTextClassifier(ChatModelAgent):
    def __init__(self, model: BaseJsonLM):
        super().__init__(model)
        self.max_chunk_size = 12000

    def classify(self, html_content: str) -> WebpageType:
        compressed_html, subs = minify_html(html_content, good_attrs={'class', 'href'})
        html_part = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(compressed_html)[0]

        system_prompt = f"""
Your goal is to classify website by HTML into 4 categories - {WebpageType.values_repr()}.
"catalog" page contains a table or a list of similar elements or cards.
"detailed_page" contains description of one product.
In other cases return "other".
Return only one category in a form of json. Example of response json:
```
{{
    "category": "catalog"
}}
```
"""
        messages = [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=html_part
            )
        ]

        def _validate_response(response: dict) -> Optional[str]:
            try:
                WebpageType(response['category'])
            except ValueError:
                return f"{response} is not a valid page type. Should be one of {WebpageType.values_repr()}"
            return None

        data: dict = self.query_with_validation(messages, _validate_response, max_retries=2)
        return WebpageType(data['category'])
