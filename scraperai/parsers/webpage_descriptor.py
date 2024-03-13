import json
import logging

from scraperai.vision.base import BaseVision
from scraperai.lm.base import BaseJsonLM
from scraperai.utils.html import split_html, HtmlPart, minify_html, remove_nodes_by_xpath


class WebpageVisionDescriptor:
    def __init__(self, model: BaseVision):
        self.model = model

    def describe(self, screenshot: str) -> str:
        system_prompt = "Your primary goal is to describe the content of the websites"
        user_prompt = """
You are given a screenshot of the webpage. Your goal is to describe the content of the webpage in one paragraph.
Do not describe common elements of all websites, such as header, footer, navigation menus. 
Make a short description without extracting concrete fields values.
It might be a page of the product, service, project or something else.
"""
        response = self.model.invoke(user_prompt, system_prompt, screenshot)
        return response


class DescribedHtmlPart(HtmlPart):
    description: str
    is_relevant: bool

    def __str__(self):
        return f"(xpath='{self.xpath}'  html_size='{self.html_size}' text_size='{self.text_size}' " \
               f"description='{self.description}') is_relevant='{self.is_relevant}'"

    def __repr__(self):
        return self.__str__()


class WebpagePartsDescriptor:
    def __init__(self, model: BaseJsonLM):
        self.model = model
        self.__minified_html = None

    def split_and_describe(self, html: str, context: str = None) -> list[DescribedHtmlPart]:
        html, _ = minify_html(html, use_substituions=False)
        self.__minified_html = html
        parts = split_html(html, max_text_size=4000)
        formtted_parts = json.dumps({part.xpath: part.text_content for part in parts}, indent=4, ensure_ascii=False)
        system_prompt = "Your primary goal is to describe the content of the websites"
        user_prompt = """
You will be given a json dict where keys are xpath and values are texts:
```
{
    "some xpath": "some text",
}
```
These texts are parts of one webpage. Give a very short description for each part and return as json in the following format:
```
{
    "some xpath": "text description",
}
```

Array of texts:
```
%s
```
""" % formtted_parts
        response = self.model.invoke_as_json(user_prompt, system_prompt)
        new_parts = []
        for part in parts:
            new_parts.append(DescribedHtmlPart(
                xpath=part.xpath,
                html_size=part.html_size,
                text_size=part.text_size,
                html_content=part.html_content,
                text_content=part.text_content,
                description=response[part.xpath],
                is_relevant=False
            ))
        return new_parts

    def find_relevant_parts(self, parts: list[DescribedHtmlPart]) -> list[DescribedHtmlPart]:
        formtted_parts = json.dumps({part.xpath: part.description for part in parts}, indent=4, ensure_ascii=False)

        system_prompt = "You are an HTML web scraper."
        user_prompt = """
Imaging you are an HTML web scraper. Your goal is to find relevant information to scrape/parse on the webpage that contains information about one item.
You are given a list of descriptions of parts of one webpage in the following json format:
```
{
    "some xpath": "text description",
}
```
Return a list of xpaths that are relevant to parse in JSON format:
```
{
    "relevant_xpaths": ["xpath1", "xpath2", ]
}
```
Descriptions data:
```
%s
```""" % formtted_parts
        response = self.model.invoke_as_json(user_prompt, system_prompt)
        relevant_xpaths = set(response['relevant_xpaths'])
        for part in parts:
            if part.xpath in relevant_xpaths:
                part.is_relevant = True
        return parts

    def find_and_remove_irrelevant_html_parts(self, html: str, context: str = None) -> str:
        parts = self.split_and_describe(html, context)
        logging.info(f'Split HTML into {len(parts)} parts')
        parts = self.find_relevant_parts(parts)
        rel_count = len([p for p in parts if p.is_relevant])
        logging.info(f'Found {rel_count}/{len(parts)} relevant HTML parts')
        xpaths_to_remove = [part.xpath for part in parts if not part.is_relevant]
        return remove_nodes_by_xpath(self.__minified_html, xpaths_to_remove)


def test_vision():
    from tests.settings import BASE_DIR, OPENAI_API_KEY
    from scraperai.vision.openai import VisionOpenAI
    descriptor = WebpageVisionDescriptor(VisionOpenAI(OPENAI_API_KEY))
    with open(BASE_DIR / 'tests' / 'data' / 'ozon_detail_page.html', 'r') as f:
        html_content = f.read()

    new_html = descriptor.describe(html_content)
    with open(BASE_DIR / 'tests' / 'data' / 'ozon_detail_page_relevant.html', 'w+') as f:
        f.write(new_html)


def test():
    from tests.settings import BASE_DIR, OPENAI_API_KEY
    from scraperai.lm.openai import JsonOpenAI
    descriptor = WebpagePartsDescriptor(JsonOpenAI(OPENAI_API_KEY, temperature=0))
    with open(BASE_DIR / 'tests' / 'data' / 'ozon_detail_page.html', 'r') as f:
        html_content = f.read()

    new_html = descriptor.find_and_remove_irrelevant_html_parts(html_content)
    with open(BASE_DIR / 'tests' / 'data' / 'ozon_detail_page_relevant.html', 'w+') as f:
        f.write(new_html)


if __name__ == '__main__':
    test()
