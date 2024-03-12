import logging

from langchain.prompts import PromptTemplate
from langchain_text_splitters import TokenTextSplitter
from lxml import html, etree

from scraperai.lm.base import BaseJsonLM
from scraperai.parsers.models import CatalogItem
from scraperai.utils.html import minify_html

logger = logging.getLogger(__file__)


class CatalogItemDetector:
    def __init__(self, model: BaseJsonLM):
        self.model = model
        self.max_chunk_size = 32000

    def detect_catalog_item(self, html_content: str, extra_prompt: str = None) -> CatalogItem | None:
        compressed_html, subs = minify_html(html_content, good_attrs={'class', 'href'})

        system_prompt = """
You are an HTML parser. You will be given an HTML page with a catalog.
Your primary goal is to find classname of these elements."""

        prompt_template = PromptTemplate.from_template("""
This HTML contains a catalog of projects. Each element includes name, image, url.
Your primary goal is to find xpath selectors of the catalog elements.
It is better to use xpath with classname.
The output should be a JSON dictionary like this:
```
{{
    "card": "xpath to select all catalog cards",
    "url": "xpath to select href urls",
}}
```
If you have not found any relevant data return:
```
{{
    "card": null,
    "url": null
}}
```
{extra_prompt}
The HTML: {html}""")
        payload = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(compressed_html)[0]
        prompt = prompt_template.format(extra_prompt=extra_prompt or '', html=payload)
        data = self.model.invoke_as_json(prompt, system_prompt)
        if data['card'] is None:
            return None

        card_xpath = data['card']
        url_xpath = data['url']
        tree = html.fromstring(compressed_html)

        # counts = {}
        # for key, xpath in data.items():
        #     counts[key] = len(xpath)
        # if len(set(counts.values())) != 1:
        #     logger.info(f'Bad counts: {counts}')
        #     return None

        html_snippet = etree.tostring(tree.xpath(card_xpath)[0],
                                      pretty_print=True,
                                      method="html",
                                      encoding='unicode')
        return CatalogItem(
            card_xpath=card_xpath,
            url_xpath=url_xpath,
            html_snippet=html_snippet,
            urls_on_page=tree.xpath(url_xpath)
        )

    def manually_change_catalog_item(self, html_content: str, card_xpath: str, url_xpath: str):
        tree = html.fromstring(html_content)
        html_snippet = etree.tostring(tree.xpath(card_xpath)[0],
                                      pretty_print=True,
                                      method="html",
                                      encoding='unicode')
        urls_on_page = tree.xpath(url_xpath)
        return CatalogItem(
            card_xpath=card_xpath,
            url_xpath=url_xpath,
            html_snippet=html_snippet,
            urls_on_page=urls_on_page
        )
