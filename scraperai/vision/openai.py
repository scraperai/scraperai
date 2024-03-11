from pathlib import Path

from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from scraperai.utils.image import encode_image_to_b64
from scraperai.vision.base import BaseVision


class VisionOpenAI(BaseVision):
    latest = 'gpt-4-vision-preview'

    def __init__(self,
                 openai_api_key: str,
                 openai_organization: str = None,
                 model_name: str = latest,
                 **kwargs):
        self.total_cost = 0.0
        self.chat = ChatOpenAI(model=model_name,
                               openai_api_key=openai_api_key,
                               openai_organization=openai_organization,
                               **kwargs)

    def invoke(self,
               user_prompt: str,
               system_prompt: str,
               image: bytes | str | Path) -> str:
        messages = [
            SystemMessage(
                content=system_prompt
            ),
            HumanMessage(
                content=[
                    {"type": "text", "text": user_prompt},
                    {
                        "type": "image_url",
                        "image_url": encode_image_to_b64(image)
                    },
                ]
            )
        ]
        with get_openai_callback() as cb:
            response = self.chat.invoke(messages).content
            self.total_cost += cb.total_cost
        return response
