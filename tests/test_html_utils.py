import unittest

from scraperai.parsers.models import WebpageFields, StaticField, DynamicField
from scraperai.parsers.utils import extract_fields_from_html, extract_items
from scraperai.utils.html import extract_dynamic_fields_by_xpath, minify_html
from .settings import DATA_DIR


class TestHtmlUtils(unittest.TestCase):
    def test_xpath_extractor(self):
        with open(DATA_DIR / 'ozon_card.html', 'r') as f:
            html_content = f.read()
        test_output = extract_dynamic_fields_by_xpath(
            labels_xpath=".//div[@class='b8a i3t']/span/font/preceding-sibling::text()[1]",
            values_xpath=".//div[@class='b8a i3t']/span/font",
            html_content=html_content
        )
        correct_output = {
            'Тип:': 'Наушники',
            'Наличие микрофона:': 'Да',
            'Конструкция наушников:': 'Внутриканальные',
            'Шумоподавление:': 'Активное',
            'Время работы в режиме разговора, ч:': '6'
        }
        self.assertEqual(test_output, correct_output)

    def test_fields_extractor(self):
        with open(DATA_DIR / 'ozon_card.html', 'r') as f:
            html_content = f.read()

        fields = WebpageFields(
            static_fields=[
                StaticField(field_name='Sale Tag', field_xpath='/html/body/div/div[1]/a/div/section/div/div/div/div'),
                StaticField(field_name='Product Name', field_xpath='//div[@class="w9i"]/a/div/span/text()'), 
                StaticField(field_name='Rating', field_xpath='//div[@class="w9i"]/div/div/span[1]/span/text()'),
                StaticField(field_name='Number of Reviews', field_xpath='//div[@class="w9i"]/div/div/span[2]/span/text()'),
                StaticField(field_name='Current Price', field_xpath='//div[@class="iw9"]/div/div/span[1]/text()'), 
                StaticField(field_name='Original Price', field_xpath='//div[@class="iw9"]/div/div/span[2]/text()'), 
                StaticField(field_name='Discount', field_xpath='//div[@class="iw9"]/div/div/span[3]/text()'), 
                StaticField(field_name='Stock Left', field_xpath='//div[@class="iw9"]/div[2]/span/text()'),
                StaticField(field_name='Delivery Date', field_xpath='//div[@class="iw9"]/div[3]/div/div/button/div/div/text()')],
            dynamic_fields=[
                DynamicField(
                    section_name='Test',
                    name_xpath=".//div[@class='b8a i3t']/span/font/preceding-sibling::text()[1]",
                    value_xpath=".//div[@class='b8a i3t']/span/font",
                )
            ]
        )
        data = extract_fields_from_html(html_content, fields)

        correct_output = {
            "Sale Tag": "РАСПРОДАЖА",
            "Product Name": "Наушники беспроводные, bluetooth наушники, tws наушники, беспроводные наушники с микрофоном, беспроводные наушники",
            "Rating": "4.7  ",
            "Number of Reviews": "178 отзывов",
            "Current Price": "1 299 ₽",
            "Original Price": "14 990 ₽",
            "Discount": "−91%",
            "Stock Left": "Осталось 89 шт",
            "Delivery Date": "Послезавтра",
            "Тип:": "Наушники",
            "Наличие микрофона:": "Да",
            "Конструкция наушников:": "Внутриканальные",
            "Шумоподавление:": "Активное",
            "Время работы в режиме разговора, ч:": "6"
        }
        self.assertEqual(data, correct_output)

    def test_nested_fields_extractor(self):
        with open(DATA_DIR / 'ozon_catalog_page.html', 'r') as f:
            html_content = f.read()
        html_content, _ = minify_html(html_content)

        fields = WebpageFields(
            static_fields=[
                StaticField(field_name='Product Name', field_xpath='//div[@class="i8v"]/a/div/span/text()'),
                StaticField(field_name='Rating', field_xpath='//div[@class="i8v"]/div/div/span[1]/span/text()'),
                StaticField(field_name='Number of Reviews', field_xpath='//div[@class="i8v"]/div/div/span[2]/span/text()')
            ],
            dynamic_fields=[
                DynamicField(
                    section_name='Test',
                    name_xpath="//div[@class='ba9 r9i']/span/font/preceding-sibling::text()[1]",
                    value_xpath="//div[@class='ba9 r9i']/span/font",
                )
            ]
        )
        items = extract_items(html_content, fields, root_xpath='.//div[@class="vi6 v6i"]')
        for item in items:
            print(item)
            print()


if __name__ == '__main__':
    unittest.main()
