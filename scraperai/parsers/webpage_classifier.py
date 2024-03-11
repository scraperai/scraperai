import enum

from scraperai.vision.base import BaseVision
from scraperai.lm.base import BaseLM


class WebpageType(str, enum.Enum):
    CATALOG = 'catalog'
    DETAILS = 'detailed_page'
    OTHER = 'other'


class WebpageVisionClassifier:
    def __init__(self, model: BaseVision):
        self.model = model

    def classify(self, screenshot: str) -> WebpageType:
        system_prompt = "Your goal is to classify webpages by screenshot."
        user_prompt = """
Your goal is to classify website by screenshot into 3 categories - "catalog", "detailed_page" or "other".
"catalog" page contains a table or a list of similar elements or cards.
"detailed_page" contains description of one product. 
In other cases return "other".
Return only category name in the answer.
"""
        response = self.model.invoke(user_prompt, system_prompt, screenshot)
        return WebpageType(response)


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
