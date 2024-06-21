import logging
from typing import Callable

from bs4 import BeautifulSoup
from langchain_core.messages import SystemMessage, HumanMessage
from lxml import html

from scraperai.llm.base import BaseJsonLM
from scraperai.parsers.agent import ChatModelAgent
from scraperai.models import Pagination
from scraperai.utils.html import minify_html, extract_field_by_xpath
from langchain_text_splitters import TokenTextSplitter


logger = logging.getLogger('scraperai')


class PaginationDetector(ChatModelAgent):
    def __init__(self, model: BaseJsonLM):
        super().__init__(model)
        self.model = model
        self.max_chunk_size = 12000

    def find_pagination(self, html_content: str):
        # TODO: Search for different pagination types
        xpath = self.find_xpath(html_content)
        if xpath:
            return Pagination(type='xpath', xpath=xpath)
        else:
            return Pagination(type='scroll')

    def find_xpath(self, html_content: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html_content: webpage source
        :return: xpath to pagination button or None if not found
        """
        return self._find_xpath(html_content)
        # TODO: Add validation that xpath really exists in HTML
        chain_methods: list[Callable[[str], str]] = [self._find_pagination_classname, self._find_pagination_name]
        for method in chain_methods:
            xpath = method(html_content)
            if xpath:
                return xpath
        return None

    def _find_xpath(self, html_content: str) -> str | None:
        html_content, subs = minify_html(html_content, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page.
    This HTML contains a list of elements and button to show more elements or to switch page.
    Text of the button can be "More", "Load more", "Next", "Next page" and any other.
    Your goal is to find XPATH to this button. This XPATH will be later used to click the button
    Return it in a json format:
    ```
    {"xpath": "some xpath"}
    ```
    If nothing found, return:
    ```
    {"xpath": null}
    ```
    """
    
        html_parts = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(html_content)
        if len(html_parts) > 2:
            html_parts = [html_parts[0], html_parts[-1]]
        for html_part in reversed(html_parts):
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=html_part)
            ]
            resp = self.model.invoke(messages)
            xpath = resp['xpath']
            if xpath is None:
                continue

            tree = html.fromstring(html_content)
            values = extract_field_by_xpath(tree, xpath)
            if not isinstance(values, list):
                return xpath
            # TODO: Check if element is clickable
            return None
    
    def _find_pagination_classname(self, html_content: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html_content: webpage source
        :return: xpath or None if not found
        """
        initial_soup = BeautifulSoup(html_content, features='lxml')
        html_content, subs = minify_html(html_content, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page.
This HTML contains a list of elements and button to show more elements or to switch page.
Text of the button can be "More", "Load more", "Next", "Next page", "Show all", and any other.
Your goal is to find classname of this button.
Return classname in a json format:
```
{"classname": "some classname"}
```
If nothing found, return:
```
{"classname": null}
```
"""

        html_parts = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(html_content)
        if len(html_parts) > 2:
            html_parts = [html_parts[0], html_parts[-1]]
        classname = None
        for html_part in reversed(html_parts):
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=html_part)
            ]
            resp = self.model.invoke(messages)
            classname = resp['classname']
            if classname:
                break
        if len(initial_soup.find_all(class_=classname)) == 1:
            return f"//*[@class='{classname}']"
        return None

    def _find_pagination_name(self, html_content: str) -> str | None:
        """
        Tries to find xpath for pagination button
        :param html_content: webpage source
        :return: xpath or None if not found
        """
        initial_soup = BeautifulSoup(html_content, features='lxml')
        html_content, subs = minify_html(html_content, good_attrs={'class'})

        system_prompt = """You are an HTML parser. Your primary goal is to find pagination on the web page.
This HTML contains a list of elements and button to show more elements.
Text of the button can be "More", "Load more", "Next page", "Next", "Show all" and so on. Your goal is to find text and tag of this button.
Return button text and tag name in a json form:
```
{
    "text": "button text",
    "tag": "tag name"
}
``` 
If nothing found, return:
```
{
    "text": null,
    "tag": null
}
```
"""

        html_parts = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(html_content)
        if len(html_parts) > 2:
            html_parts = [html_parts[0], html_parts[-1]]
        result = None
        for html_part in html_parts:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=html_part)
            ]
            resp = self.model.invoke(messages)
            if resp['tag'] is not None:
                result = resp
                break

        if result is None:
            return None

        tag, button_text = result['tag'], result['text']
        buttons = initial_soup.find_all(lambda t: t.name == tag and button_text in t.text)
        if len(buttons) == 1:
            return f"//{tag}[text()='{button_text}']"
        else:
            return None
