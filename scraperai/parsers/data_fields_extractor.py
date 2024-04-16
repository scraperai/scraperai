import logging
from typing import Optional

from langchain_core.messages import SystemMessage, HumanMessage
from lxml import html
from pydantic import BaseModel, ValidationError

from scraperai.lm.base import BaseJsonLM
from scraperai.parsers.agent import ChatModelAgent
from scraperai.models import StaticField, WebpageFields, DynamicField
from scraperai.parsers.utils import build_validation_error_message
from scraperai.utils.html import minify_html, extract_field_by_xpath, extract_dynamic_fields_by_xpath

logger = logging.getLogger('scraperai')


class StaticFieldResponseModel(BaseModel):
    fields: list[StaticField]


class DynamicFieldResponseModel(BaseModel):
    fields: list[DynamicField]


class DataFieldsExtractor(ChatModelAgent):
    def __init__(self, model: BaseJsonLM):
        super().__init__(model)
        self.model = model

    def extract_static_fields(self, html_content: str, context: str = None) -> list[StaticField]:
        html_snippet, _ = minify_html(html_content, use_substituions=False)

        system_prompt = """
You are an HTML parser. You will be given an HTML snippet that contains information about one element. 
This element can be a product, service, project or something else.

There are two types of data fields in HTML snippets. First type is static field that do not contain field name.
It can be both single values and arrays.
Second type is dynamic sections where there are both field names and values mentioned.
Use relevant XPATH that selects nodes by classname, id or some other attribute.
Extract static data fields and present results as JSON with the following structure:
```
{
    "fields": [
        {"field_name": "guessed by you, Human Readable", "field_xpath": "xpath to field value"},
    ]
}
```
If nothing found return empty array"""
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=html_snippet),
        ]
        if context:
            messages.append(HumanMessage(content=context))

        tree = html.fragment_fromstring(html_snippet, create_parent=True)

        def extract_fields_from_response(json_data: dict) -> list[StaticField]:
            model = StaticFieldResponseModel(**json_data)
            for i in range(len(model.fields)):
                mod_xpath = '.' + model.fields[i].field_xpath.lstrip('.')
                model.fields[i].first_value = extract_field_by_xpath(tree, mod_xpath)
            return model.fields

        def _validate_response(json_data: dict) -> Optional[str]:
            try:
                extract_fields_from_response(json_data)
            except ValidationError as exc:
                return build_validation_error_message(exc)
            return None

        response = self.query_with_validation(messages, _validate_response)
        return extract_fields_from_response(response)

    def extract_dynamic_fields(self, html_content: str, context: str = None) -> list[DynamicField]:
        html_snippet, _ = minify_html(html_content, use_substituions=False)
        system_prompt = """
You are an HTML parser. You will be given an HTML snippet that contains information about one element. 
This element can be a product, service, project or something else.

There are two types of data fields in HTML snippets. First type is static field that do not contain field name.
Second type is dynamic sections where there are both field names and values mentioned. 
It is very important that dynamic section includes fields with both NAME and VALUE specified.

Extract dynamic sections data fields in JSON format:
```
{
    "fields": [
        {
            "section_name": "guessed by you, Human Readable", 
            "name_xpath": "xpath relative to section to extract ALL names or labels of fields",
            "value_xpath": "xpath relative to section to extract ALL values of fields"
        },
    ]
}
```
If nothing found return empty array.
XPATHs should start with ".//".
"""

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=html_snippet),
        ]
        if context:
            messages.append(HumanMessage(content=context))

        tree = html.fromstring(html_content)

        def extract_fields_from_response(json_data: dict) -> list[DynamicField]:
            model = DynamicFieldResponseModel(**json_data)
            for i in range(len(model.fields)):
                model.fields[i].first_values = extract_dynamic_fields_by_xpath(
                    model.fields[i].name_xpath,
                    model.fields[i].value_xpath,
                    tree=tree
                )
            return model.fields

        def _validate_response(json_data: dict) -> Optional[str]:
            try:
                extract_fields_from_response(json_data)
            except ValidationError as exc:
                return build_validation_error_message(exc)
            except ValueError as exc:
                return exc.__str__()
            return None

        data = self.query_with_validation(messages, _validate_response)
        return extract_fields_from_response(data)

    def extract_fields(self, html_snippet: str) -> WebpageFields:
        static_fields = self.extract_static_fields(html_snippet)
        static_fields_str = ', '.join([f'({f.field_name}: {f.field_xpath})' for f in static_fields])
        dynamic_fields = self.extract_dynamic_fields(
            html_snippet,
            context=f'You have already found this static fields: {static_fields_str}. Do not add them.'
        )
        # print(type(static_fields))
        # print(type(static_fields[0]))
        return WebpageFields(static_fields=static_fields, dynamic_fields=dynamic_fields)

    def find_fields(self, html_snippet: str, user_description: str) -> WebpageFields:
        static_fields = self.extract_static_fields(html_snippet, user_description)
        if static_fields:
            return WebpageFields(static_fields=static_fields, dynamic_fields=[])
        dynamic_fields = self.extract_dynamic_fields(html_snippet, user_description)
        return WebpageFields(static_fields=[], dynamic_fields=dynamic_fields)
