import unittest
from pathlib import Path

from scraperai.llm import OpenAIChatModel, OpenAIModel
from .settings import OPEN_AI_TOKEN

DATA_DIR = Path(__file__).resolve().parent / 'data'


class CatalogCardsTests(unittest.TestCase):
    def test_detection(self):
        from scraperai.parsing.catalog_card import CatalogCardParser

        parser = CatalogCardParser(OpenAIChatModel(OPEN_AI_TOKEN, OpenAIModel.gpt4))

        with open(DATA_DIR / 'ozon_card.html', 'r') as f:
            html_str = f.read()

        result = parser.find_fields(html_str)
        print(result)
        self.assertTrue('fields_with_keys' in result)
        self.assertTrue('fields_without_keys' in result)

    def test_xpath_extraction(self):
        ...
        # tree = html.fromstring(html_str)
        # for item in result['fields_with_keys']:
        #     self.assertEqual(tree.xpath(item['key_xpath'])[0].strip(), item['key'])
        #     self.assertEqual(tree.xpath(item['value_xpath'])[0].strip(), item['value'])


if __name__ == '__main__':
    unittest.main()
