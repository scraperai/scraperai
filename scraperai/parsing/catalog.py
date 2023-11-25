import json
import logging

import pandas as pd
from bs4 import BeautifulSoup

from scraperai.utils import markdown_to_pandas, cut_large_request
from scraperai.llm.chat import OpenAIModel, OpenAIChatModel
from scraperai.utils.compressor import compress_html


logger = logging.getLogger(__file__)


class CatalogParser:
    def __init__(self, chat_model: OpenAIChatModel = None):
        if chat_model:
            self.chat_model = chat_model
        else:
            self.chat_model = OpenAIChatModel(model=OpenAIModel.gpt4)

    def to_table(self, html: str) -> pd.DataFrame | None:
        html, subs = compress_html(html)
        system_prompt = "You are an HTML parser. Your primary goal is to extract " \
                        "relevant data from HTML in a Markdown table. " \
                        "The output should only include Markdown table and no other text"
        prompt = f"""This HTML contains a list of elements describing programms. Extract this list and present
            it as a table with columns: name, description, price, image. The HTML: {html}"""
        text = self.chat_model.get_answer(prompt, system_prompt)
        return markdown_to_pandas(text, subs)

    def catalog_to_code(self, html: str) -> str:
        compressed_html, subs = compress_html(html)

        system_prompt = "You are an HTML parser. Your primary goal is write python code using BeautifulSoup library. " \
                        "The output should only include python code."
        prompt = f"This HTML contains a list of elements describing programms. " \
                 f"Write python code to extract data using BeautifulSoup. " \
                 f"Data includes: name, description, price, image. The HTML: {html}"

        max_tokens = 1000
        payload = cut_large_request(self.chat_model.model, system_prompt, prompt, compressed_html, max_tokens)
        text = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens)
        return text

    def find_classnames(self, html: str, search_elements: list[str]) -> dict[str, str] | None:
        initial_soup = BeautifulSoup(html, features='lxml')
        compressed_html, subs = compress_html(html, good_attrs={'class'})

        search_elements = ','.join([f'"{x}"' for x in search_elements])
        system_prompt = "You are an HTML parser. You will be given an HTML page with a catalog." \
                        "Your primary goal is to find class name of these elements. " \
                        "The output should only a dictionary include a dictionary of class names in JSON format"
        prompt = 'This HTML contains a catalog of projects. Each element includes name, description.' \
                 'Your primary goal is to find class names of these elements. ' \
                 f'The output should only include a JSON dictionary where keys are {search_elements} ' \
                 'and values are class names. If you have not found any relevant data return "None"' \
                 "The HTML: %s"
        max_tokens = 200
        payload = cut_large_request(self.chat_model.model, system_prompt, prompt, compressed_html, max_tokens)
        text = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens)
        try:
            data = json.loads(text)
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
            logger.error(f'Wrong response format: {text}')
            logger.exception(e)
            return None

