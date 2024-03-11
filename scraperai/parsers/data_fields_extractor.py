import io
import logging
import re

import numpy as np
import pandas as pd

from scraperai.lm.base import BaseLM
from scraperai.parsers.models import StaticField, WebpageFields, DynamicField
from scraperai.utils.html import minify_html

logger = logging.getLogger(__file__)


class DataFieldsExtractor:
    def __init__(self, model: BaseLM):
        self.model = model

    def extract_static_fields(self, html: str, context: str = None) -> list[StaticField]:
        html_snippet, _ = minify_html(html, use_substituions=False)

        system_prompt = "You are an HTML parser. Your primary goal is to find fields with data."
        prompt = """
You are an HTML parser. You will be given an HTML snippet that contains information about one element. 
This element can be a product, service, project or something else.

There are two types of data fields in HTML snippets. First type is static field that do not contain field name.
It can be both single values and arrays.
Second type is dynamic sections where there are both field names and values mentioned.

Extract static data fields.
Please, extract only static sections in CSV format. You need to mention: 
1. "field_name": guessed by you, Human Readable 
2. "field_xpath" : xpath to field value
3. "field_type": type of field "single" or "array"
4. "iterator_xpath": selector inside the array section for extract array elements

Use , as csv separator. Do not add any extra symbols.
The HTML: %s
""" % html_snippet
        response = self.model.invoke(prompt, system_prompt)
        df = pd.read_csv(io.StringIO(response), header=0, delimiter=',').replace(np.nan, None)
        return [
            StaticField(
                field_name=row['field_name'],
                field_xpath=row['field_xpath'],
                field_type=re.sub('[^A-Za-z0-9]+', '', row['field_type']),
                iterator_xpath=row['iterator_xpath'],
            )
            for _, row in df.iterrows()
        ]

    def extract_dynamic_fields(self, html: str, context: str = None) -> list[DynamicField]:
        html_snippet, _ = minify_html(html, use_substituions=False)

        system_prompt = "You are an HTML parser. Your primary goal is to find fields with data."
        prompt = """
You are an HTML parser. You will be given an HTML snippet that contains information about one element. 
This element can be a product, service, project or something else.

There are two types of data fields in HTML snippets. First type is static field that do not contain field name.
Second type is dynamic sections where there are both field names and values mentioned. 
It is very important that dynamic section includes fields with both NAME and VALUE specified.

Extract dynamic sections data fields in CSV format. You need to mention: 
1. section_name: guessed by you, Human Readable 
3. name_xpath - xpath relative to section to extract ALL names or labels of fields
4. value_xpath - xpath relative to section to extract ALL values of fields

First row must be columns names: section_name, name_xpath, value_xpath.

XPATHs should start with ".//".
Use , as csv separator. Do not add any extra symbols.
The HTML: %s
""" % html_snippet

        response = self.model.invoke(prompt, system_prompt)
        df = pd.read_csv(io.StringIO(response), header=0, delimiter=',').replace(np.nan, None)
        try:
            return [
                DynamicField(
                    section_name=row['section_name'],
                    name_xpath=row['name_xpath'],
                    value_xpath=row['value_xpath'],
                )
                for _, row in df.iterrows()
            ]
        except KeyError as e:
            print(response)
            print(df)
            raise e

    def extract_fields(self, html_snippet: str) -> WebpageFields:
        static_fields = self.extract_static_fields(html_snippet)
        dynamic_fields = self.extract_dynamic_fields(html_snippet)
        return WebpageFields(static_fields=static_fields, dynamic_fields=dynamic_fields)


def test():
    from tests.settings import BASE_DIR, OPEN_AI_TOKEN
    from scraperai.lm.openai import OpenAI
    parser = DataFieldsExtractor(OpenAI(OPEN_AI_TOKEN, temperature=0))

    with open(BASE_DIR / 'tests' / 'data' / 'ozon_card.html', 'r') as f:
        html_content = f.read()
    # Static fields
    result = parser.extract_static_fields(html_content)
    for el in result:
        print(el)


if __name__ == '__main__':
    test()
