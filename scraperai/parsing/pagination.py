import logging
from typing import Callable

from bs4 import BeautifulSoup
from scraperai.utils import split_large_request
from scraperai.llm import OpenAIChatModel
from scraperai.utils.compressor import compress_html


logger = logging.getLogger(__file__)


class PaginationDetector:
    def __init__(self, chat_model: OpenAIChatModel):
        self.chat_model = chat_model
        self.total_spent = 0.0

    def find_xpath(self, html: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html: webpage source
        :return: xpath to pagination button or None if not found
        """
        chain_methods: list[Callable[[str], str]] = [self._find_pagination_classname, self._find_pagination_name]
        for method in chain_methods:
            xpath = method(html)
            if xpath:
                return xpath
        return None

    def _find_pagination_classname(self, html: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html: webpage source
        :return: xpath or None if not found
        """
        initial_soup = BeautifulSoup(html, features='lxml')
        html, subs = compress_html(html, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page."""
        prompt = f'This HTML contains a list of elements and button to show more elements. ' \
                 f'Text of the button can be "More", "Load more", "Еще", "Показать еще", "Дальше", ' \
                 f'"Следующая страница". Your goal is to find classname of this button. ' \
                 f'Return classname if found or "None" instead, no other words. The HTML: %s'

        max_tokens = 100
        payloads = split_large_request(self.chat_model.model, system_prompt, prompt, html, max_tokens)

        classname = 'None'
        for payload in payloads:
            response = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens=max_tokens)
            self.total_spent += response.price
            text = response.text
            if text != 'None':
                classname = text
        if len(initial_soup.find_all(class_=classname)) == 1:
            return f"//*[@class='{classname}']"
        return None

    def _find_pagination_name(self, html: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html: webpage source
        :return: xpath or None if not found
        """
        initial_soup = BeautifulSoup(html, features='lxml')
        html, subs = compress_html(html, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page."""
        prompt = 'This HTML contains a list of elements and button to show more elements. ' \
                 'Text of the button can be "More", "Load more", "Показать еще", ' \
                 '"Еще", "Дальше", "Следующая страница". Your goal is to find text and tag of this button. ' \
                 'Return button text and tag in a form "text,tag" if found or "None" instead, no other words. ' \
                 'The HTML: %s'

        max_tokens = 100
        payloads = split_large_request(self.chat_model.model, system_prompt, prompt, html, max_tokens)

        result = 'None'
        for payload in payloads:
            response = self.chat_model.get_answer(prompt % payload, system_prompt, max_tokens=max_tokens)
            self.total_spent += response.price
            text = response.text
            if text != 'None':
                result = text
        if result == 'None' or len(result.split(',')) != 2:
            logger.error(f'Wrong response: {result}')
            return None
        name, tag = result.split(',')
        buttons = initial_soup.find_all(lambda t: t.name == tag and name in t.text)
        if len(buttons) == 1:
            return f"//{tag}[text()='{name}']"
        else:
            logger.error(f'Wrong response: {result}')
            return None
