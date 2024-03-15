import unittest

from scraperai.parsers import DataFieldsExtractor
from scraperai.lm.openai import JsonOpenAI
from scraperai.utils import html
from .settings import OPENAI_API_KEY, DATA_DIR


json_openai_model = JsonOpenAI(OPENAI_API_KEY, temperature=0)


class TextExtractors(unittest.TestCase):
    def test_static_fields_extractor(self):
        parser = DataFieldsExtractor(json_openai_model)
        with open(DATA_DIR / 'ozon_card.html', 'r') as f:
            html_content = f.read()
        static_fields = parser.extract_static_fields(html_content)
        for f in static_fields:
            print(f)

    def test_dynamic_fields_extractor(self):
        parser = DataFieldsExtractor(json_openai_model)

        with open(DATA_DIR / 'ozon_card.html', 'r') as f:
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
