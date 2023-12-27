import json
import logging

import pandas as pd
from bs4 import BeautifulSoup

from scraperai.utils import markdown_to_pandas, cut_large_request
from scraperai.llm import OpenAIChatModel
from scraperai.utils.compressor import compress_html


logger = logging.getLogger(__file__)


class CatalogParser:
    def __init__(self, chat_model: OpenAIChatModel):
        self.chat_model = chat_model
        self.total_spent = 0.0

    def to_table(self, html: str) -> pd.DataFrame | None:
        html, subs = compress_html(html)
        system_prompt = "You are an HTML parser. Your primary goal is to extract " \
                        "relevant data from HTML in a Markdown table. " \
                        "The output should only include Markdown table and no other text"
        prompt = f"""This HTML contains a list of elements describing programms. Extract this list and present
            it as a table with columns: name, description, price, image. The HTML: {html}"""
        response = self.chat_model.get_answer(prompt, system_prompt)
        self.total_spent += response.price
        return markdown_to_pandas(response.text, subs)

    def find_classnames(self, html: str) -> dict[str, str] | None:
        """

        :param html: raw html
        :return: {
            "card": "catalog card's classname",
            "url": "classname of element containing href url",
        }
        """
        initial_soup = BeautifulSoup(html, features='lxml')
        compressed_html, subs = compress_html(html, good_attrs={'class'})

        system_prompt = "You are an HTML parser. You will be given an HTML page with a catalog." \
                        "Your primary goal is to find classname of these elements. "
        prompt = """
        This HTML contains a catalog of projects. Each element includes name, image, url.
        Your primary goal is to find classnames of the catalog elements.
        The output should be a JSON dictionary like this:
        ```
        {
            "card": "catalog card's classname",
            "url": "classname of element containing href url",
        }
        ```
        If you have not found any relevant data return "null"
        The HTML: %s
        """
        max_tokens = 200
        payload = cut_large_request(self.chat_model.model, system_prompt, prompt, compressed_html, max_tokens)
        response = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens=max_tokens, force_json=True)
        self.total_spent += response.price
        try:
            data = json.loads(response.text)
            if not isinstance(data, dict):
                raise TypeError

            counts = {}
            for key, value in data.items():
                counts[key] = len(initial_soup.find_all(class_=value))
            if len(set(counts.values())) != 1:
                logger.info(f'Bad counts: {counts}')
                return None

            return data
        except json.JSONDecodeError as e:
            logger.error(f'Wrong response format: {response.text}')
            logger.exception(e)
            return None
