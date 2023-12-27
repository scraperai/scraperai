import json
import logging

from bs4 import BeautifulSoup
from lxml import etree

from scraperai.llm import OpenAIChatModel
from scraperai.utils import markdown_to_pandas, cut_large_request
from scraperai.utils.compressor import compress_html

logger = logging.getLogger(__file__)


class DetailsPageParser:
    def __init__(self, chat_model: OpenAIChatModel):
        self.chat_model = chat_model
        self.total_spent = 0.0

    def to_table(self, html: str):
        compressed_html, subs = compress_html(html, good_attrs={'class'})
        system_prompt = "You are an HTML parser. Your primary goal is to extract relevant data " \
                        "from HTML in a Markdown table. The output should only include Markdown " \
                        "table and no other text"
        prompt = f"This HTML contains information about only one company. " \
                 f"Extract data and present it as a table with one row. The HTML: %s"
        max_tokens = 1000
        payload = cut_large_request(self.chat_model.model, system_prompt, prompt, compressed_html, max_tokens)
        response = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens=max_tokens)
        self.total_spent += response.price
        return markdown_to_pandas(response.text, subs)

    def to_selectors(self, html: str) -> dict[str, str] | None:
        """

        :param html:
        :return: dictionary where keys = data column names and values are xpath selectors
        """
        soup = BeautifulSoup(html, features='lxml')
        dom = etree.HTML(str(soup))

        compressed_html, subs = compress_html(html, good_attrs={'class'})

        df = self.to_table(html)
        columns_str = ','.join([f'"{x}"' for x in df.columns])
        system_prompt = 'You are an HTML parser. Your primary goal is to find xpath selectors.'
        prompt = f'This HTML contains information about only one company. ' \
                 f'This information includes {columns_str}. ' \
                 f'Your goal is to find xpath selectors to these elements. ' \
                 f'The output should only include a JSON dictionary where keys are {columns_str} and ' \
                 f'values are xpath selectors. Do not write any extra text. ' \
                 f'If you have not found any relevant data return "None". The HTML: %s'

        max_tokens = 1000
        payload = cut_large_request(self.chat_model.model, system_prompt, prompt, compressed_html, max_tokens)
        response = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens=max_tokens, force_json=True)
        self.total_spent += response.price
        try:
            data = json.loads(response.text)
            if not isinstance(data, dict):
                raise TypeError

            # Check xpath validity
            total_keys = len(data)
            errors_count = 0
            for key, xpath in data.copy().items():
                if len(dom.xpath(xpath)) == 0:
                    errors_count += 1
                    del data[key]

            if errors_count > int(0.3 * total_keys):
                raise Exception(f'Too many invalid xpaths. Response: {response.text}')

            return data
        except Exception as e:
            logger.error(f'Wrong response format: {response.text}')
            logger.exception(e)
            return None
