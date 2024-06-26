import logging

from scraperai.llm.base import BaseVision, BasePythonCodeLM
from scraperai.llm.openai import JsonOpenAI, VisionOpenAI, PythonCodeOpenAI
from scraperai.parsers import (
    PaginationDetector,
    WebpageVisionClassifier,
    WebpageTextClassifier,
    WebpagePartsDescriptor,
    WebpageVisionDescriptor,
    CatalogItemDetector,
    DataFieldsExtractor
)
from scraperai.models import WebpageFields, CatalogItem, Pagination, WebpageType
from scraperai.utils.constants import COLORS
from scraperai.utils.urls import fix_relative_url
from scraperai.utils.image import compress_b64_image

logger = logging.getLogger('scraperai')


class ParserAI:
    def __init__(self,
                 json_lm_model: JsonOpenAI = None,
                 vision_model: BaseVision = None,
                 code_model: BasePythonCodeLM = None,
                 openai_api_key: str = None,
                 openai_organization: str = None):

        if json_lm_model is None:
            self.json_lm_model = JsonOpenAI(openai_api_key, openai_organization, temperature=0)
        else:
            self.json_lm_model = json_lm_model

        if vision_model is None:
            self.vision_model = VisionOpenAI(openai_api_key, openai_organization, temperature=0)
        else:
            self.vision_model = vision_model

        if code_model is None:
            self.code_model = PythonCodeOpenAI(openai_api_key, openai_organization)
        else:
            self.code_model = code_model

    @property
    def total_cost(self) -> float:
        cost = 0.0
        if isinstance(self.json_lm_model, JsonOpenAI):
            cost += self.json_lm_model.total_cost
        if isinstance(self.vision_model, VisionOpenAI):
            cost += self.vision_model.total_cost
        return cost

    def detect_page_type(self, page_source: str | None = None, screenshot: str | None = None) -> WebpageType:
        if screenshot is not None:
            screenshot = compress_b64_image(screenshot, aspect_ratio=0.5)
            return WebpageVisionClassifier(model=self.vision_model).classify(screenshot)
        elif page_source is not None:
            return WebpageTextClassifier(model=self.json_lm_model).classify(page_source)
        else:
            raise ValueError('One of page_source, screenshot must not be None')

    def detect_pagination(self, page_source: str) -> Pagination:
        detector = PaginationDetector(model=self.json_lm_model)
        try:
            return detector.find_pagination(page_source)
        except:
            return Pagination(type='none')

    def detect_catalog_item(self, page_source: str, website_url: str, extra_prompt: str = None) -> CatalogItem | None:
        detector = CatalogItemDetector(model=self.json_lm_model)
        item = detector.detect_catalog_item(page_source, extra_prompt)
        item.urls_on_page = [fix_relative_url(website_url, u) for u in item.urls_on_page]
        return item

    def manually_change_catalog_item(self, page_source: str, card_xpath: str, url_xpath: str, website_url: str):
        detector = CatalogItemDetector(model=self.json_lm_model)
        item = detector.manually_change_catalog_item(page_source, card_xpath, url_xpath)
        item.urls_on_page = [fix_relative_url(website_url, u) for u in item.urls_on_page]
        return item

    def set_fields_colors(self, fields: WebpageFields) -> WebpageFields:
        index_color = 0
        for i in range(len(fields.static_fields)):
            fields.static_fields[i].color = COLORS[index_color % len(COLORS)]
            index_color += 1
        for i in range(len(fields.dynamic_fields)):
            fields.dynamic_fields[i].color = COLORS[index_color % len(COLORS)]
            index_color += 1
        return fields

    def extract_fields(self, html_snippet: str) -> WebpageFields:
        fields = DataFieldsExtractor(model=self.json_lm_model).extract_fields(html_snippet)
        return self.set_fields_colors(fields)

    def find_fields(self, html_snippet: str, user_description: str) -> WebpageFields:
        context = f"IMPORTANT! Search for fields that are described in " \
                  f"the following very important instructions: {user_description}"
        fields = DataFieldsExtractor(model=self.json_lm_model).find_fields(html_snippet, context)
        return self.set_fields_colors(fields)

    def summarize_details_page_as_valid_html(self, page_source: str, screenshot: str | None = None) -> str:
        if screenshot is not None:
            # Generate webpage description to give GPT some context
            description = WebpageVisionDescriptor(model=self.vision_model).describe(screenshot)
        else:
            description = None

        # Split html into pieces, describe each piece, mark pieces as relevant/irrelevant,
        # remove irrelevant pieces and return new html
        parts_descriptor = WebpagePartsDescriptor(model=self.json_lm_model)
        return parts_descriptor.find_and_remove_irrelevant_html_parts(page_source, context=description)
