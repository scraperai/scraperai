import unittest
from pathlib import Path

from scraperai.parsers import DataFieldsExtractor
from scraperai.lm.openai import OpenAI, JsonOpenAI
from scraperai.utils import html
from .settings import OPEN_AI_TOKEN, BASE_DIR


openai_model = OpenAI(OPEN_AI_TOKEN)
json_openai_model = JsonOpenAI(OPEN_AI_TOKEN)


class TextExtractors(unittest.TestCase):
    def test_static_fields_extractor(self):
        parser = DataFieldsExtractor(OpenAI(OPEN_AI_TOKEN, temperature=0))
        with open(BASE_DIR / 'tests' / 'data' / 'ozon_card.html', 'r') as f:
            html_content = f.read()
        static_fields = parser.extract_static_fields(html_content)
        print(static_fields)

    def test_dynamic_fields_extractor(self):
        parser = DataFieldsExtractor(OpenAI(OPEN_AI_TOKEN, temperature=0))

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
