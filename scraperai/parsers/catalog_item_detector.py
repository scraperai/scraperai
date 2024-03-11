import json
import logging

from bs4 import BeautifulSoup
from langchain_text_splitters import TokenTextSplitter

from scraperai.lm.base import BaseJsonLM
from scraperai.utils.html import minify_html

logger = logging.getLogger(__file__)


class CatalogItemDetector:
    def __init__(self, model: BaseJsonLM):
        self.model = model
        self.max_chunk_size = 32000

    def find_classnames(self, html: str) -> dict[str, str] | None:
        """
        :param html: raw html
        :return: {
            "card": "catalog card's classname",
            "url": "classname of element containing href url",
        }
        """
        initial_soup = BeautifulSoup(html, features='lxml')
        compressed_html, subs = minify_html(html, good_attrs={'class'})

        system_prompt = """
You are an HTML parser. You will be given an HTML page with a catalog.
Your primary goal is to find classname of these elements."""
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
If you have not found any relevant data return:
```
{
    "card": null,
    "url": null
}
The HTML: %s
        """
        payload = TokenTextSplitter(chunk_size=self.max_chunk_size).split_text(compressed_html)[0]
        try:
            data = self.model.invoke_as_json(prompt % payload, system_prompt)

            counts = {}
            for key, value in data.items():
                counts[key] = len(initial_soup.find_all(class_=value))
            if len(set(counts.values())) != 1:
                logger.info(f'Bad counts: {counts}')
                return None

            return data
        except json.JSONDecodeError as e:
            logger.error(e)
            return None
