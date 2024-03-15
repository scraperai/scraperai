import logging
from typing import Callable

from bs4 import BeautifulSoup
from scraperai.lm.base import BaseLM
from scraperai.parsers.agent import ChatModelAgent
from scraperai.parsers.models import Pagination
from scraperai.utils.html import minify_html
from langchain_text_splitters import TokenTextSplitter


logger = logging.getLogger(__file__)


class PaginationDetector(ChatModelAgent):
    def __init__(self, model: BaseLM):
        super().__init__(model)
        self.model = model
        self.max_chunk_size = 24000

    def find_pagination(self, html: str):
        # TODO: Search for different pagination types
        xpath = self.find_xpath(html)
        if xpath:
            return Pagination(type='xpath', xpath=xpath)
        else:
            return Pagination(type='scroll')

    def find_xpath(self, html: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html: webpage source
        :return: xpath to pagination button or None if not found
        """

        # TODO: Add validation that xpath really exists in HTML
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
        html, subs = minify_html(html, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page."""
        prompt = f"""
This HTML contains a list of elements and button to show more elements.
Text of the button can be "More", "Load more", "Еще", "Показать еще", "Дальше", "Следующая страница". 
Your goal is to find classname of this button.
Return classname if found or "None" instead, no other words. 
The HTML: %s
"""

        payloads = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(html)
        classname = 'None'
        for payload in reversed(payloads):
            text = self.model.invoke(prompt % payload, system_prompt)
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
        html, subs = minify_html(html, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page."""
        prompt = """
This HTML contains a list of elements and button to show more elements.
Text of the button can be "More", "Load more", "Показать еще", 
"Еще", "Дальше", "Следующая страница". Your goal is to find text and tag of this button.
Return button text and tag in a form "text,tag" if found or "None" instead, no other words.
The HTML: %s 
"""

        payloads = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(html)
        result = 'None'
        for payload in payloads:
            text = self.model.invoke(prompt % payload, system_prompt)
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
