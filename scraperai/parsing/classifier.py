import enum

from scraperai.llm import OpenAIModel, OpenAIChatModel


class WebpageType(str, enum.Enum):
    CATALOG = 'catalog'
    DETAILS = 'detailed_page'
    OTHER = 'other'


class GPTWebpageClassifier:
    def __init__(self, api_key: str):
        self.chat_model = OpenAIChatModel(api_key, model=OpenAIModel.vision)
        self.total_spent = 0.0

    def classify(self, screenshot: str) -> WebpageType:
        system_prompt = 'Your goal is to classify webpages by screenshot.'
        user_prompt = 'Your goal is to classify website by screenshot into ' \
                      '3 categories - "catalog", "detailed_page" or "other". ' \
                      '"catalog" page contains a table or a list of similar elements or cards. ' \
                      '"detailed_page" contains description of one product. ' \
                      'In other cases return "other".' \
                      'Return only category name in the answer.'
        response = self.chat_model.get_answer(user_prompt, system_prompt, screenshot, max_tokens=100)
        self.total_spent += response.price
        return WebpageType(response.text)
