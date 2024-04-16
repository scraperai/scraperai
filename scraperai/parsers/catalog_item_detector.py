import logging
from typing import Any, Optional

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_text_splitters import TokenTextSplitter
from lxml import html, etree
from pydantic import BaseModel, ValidationError

from scraperai.exceptions import NotFoundError
from scraperai.lm.base import BaseJsonLM
from scraperai.parsers.agent import ChatModelAgent
from scraperai.models import CatalogItem
from scraperai.parsers.utils import build_validation_error_message
from scraperai.utils.html import minify_html

logger = logging.getLogger('scraperai')


class CatalogItemResponseModel(BaseModel):
    card: Optional[str]
    url: Optional[str]


class CatalogItemDetector(ChatModelAgent):
    def __init__(self, model: BaseJsonLM):
        super().__init__(model)
        self.model = model
        self.max_chunk_size = 32000

    def detect_catalog_item(self, html_content: str, extra_prompt: str = None) -> CatalogItem:
        compressed_html, subs = minify_html(html_content, good_attrs={'class', 'href'})
        tree = html.fromstring(compressed_html)

        system_prompt = """
You are an HTML parser. You will be given an HTML page with a catalog.
Your primary goal is to find classname of these elements.
The HTML contains a catalog of projects. Each element includes name, image, url.
Your primary goal is to find xpath selectors of the catalog elements.
It is better to use xpath with classname.
The output should be a JSON dictionary like this:
```
{
    "card": "xpath to select all catalog cards",
    "url": "xpath to select href urls",
}
```
If you have not found any relevant data return:
```
{
    "card": null,
    "url": null
}
```"""
        html_part = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(compressed_html)[0]
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=html_part),
        ]
        if extra_prompt:
            messages.append(HumanMessage(content=extra_prompt))

        def _validate_catalog_item(response: Any) -> Optional[str]:
            # Validate schema
            try:
                model = CatalogItemResponseModel(**response)
            except ValidationError as exc:
                return build_validation_error_message(exc)
            if model.card is None or model.url is None:
                return None
            # Validate xpath
            cards_count = len(tree.xpath(model.card))
            urls_count = len(tree.xpath(model.url))
            if cards_count != urls_count:
                return f'Card xpath: "{model.card}" and url xpath: "{model.url}" are bad ' \
                       f'because the number of elements the select are different: {cards_count} != {urls_count}'
            return None

        data: dict[str, str] = self.query_with_validation(messages, _validate_catalog_item, max_retries=2)
        card_xpath = data['card']
        url_xpath = data['url']
        if card_xpath is None or url_xpath is None:
            raise NotFoundError

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
