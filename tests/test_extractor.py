import unittest
from pathlib import Path

from scraperai.parsers import DataFieldsExtractor
from scraperai.lm.openai import OpenAI, JsonOpenAI
from scraperai.utils import html
from .settings import OPENAI_API_KEY, BASE_DIR


openai_model = OpenAI(OPENAI_API_KEY)
json_openai_model = JsonOpenAI(OPENAI_API_KEY)


class TextExtractors(unittest.TestCase):
    def test_static_fields_extractor(self):
        parser = DataFieldsExtractor(OpenAI(OPENAI_API_KEY, temperature=0))
        with open(BASE_DIR / 'tests' / 'data' / 'ozon_card.html', 'r') as f:
            html_content = f.read()
        static_fields = parser.extract_static_fields(html_content)
        print(static_fields)

    def test_dynamic_fields_extractor(self):
        parser = DataFieldsExtractor(OpenAI(OPENAI_API_KEY, temperature=0))

        with open(BASE_DIR / 'tests' / 'data' / 'ozon_card.html', 'r') as f:
            html_content = f.read()

        dynamic_fields = parser.extract_dynamic_fields(html_content)
        dynamic_field = dynamic_fields[0]
        print(dynamic_field)
        test_output = html.extract_dynamic_fields_by_xpath(dynamic_field.name_xpath,
                                                           dynamic_field.value_xpath,
                                                           html_content=html_content)
        correct_output = {
            'Тип:': 'Наушники',
            'Наличие микрофона:': 'Да',
            'Конструкция наушников:': 'Внутриканальные',
            'Шумоподавление:': 'Активное',
            'Время работы в режиме разговора, ч:': '6'
        }
        self.assertEqual(test_output, correct_output)


if __name__ == '__main__':
    unittest.main()
