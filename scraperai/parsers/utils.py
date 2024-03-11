from typing import Any

from lxml import html

from scraperai.parsers.models import WebpageFields
from scraperai.utils.html import extract_dynamic_fields_by_xpath, get_node_text


def extract_fields_from_tree(tree, fields: WebpageFields, select_context_node: bool = False) -> dict[str, Any]:
    def prepare_xpath(xpath: str) -> str:
        if select_context_node and xpath.startswith('//'):
            return '.' + xpath
        return xpath

    data = {}
    for field in fields.static_fields:
        nodes = [get_node_text(node) for node in tree.xpath(prepare_xpath(field.field_xpath))]
        if len(nodes) == 0:
            value = None
        elif len(nodes) == 1:
            value = nodes[0]
        else:
            value = nodes
        data[field.field_name] = value
    for field in fields.dynamic_fields:
        items = extract_dynamic_fields_by_xpath(
            prepare_xpath(field.name_xpath),
            prepare_xpath(field.value_xpath),
            tree=tree
        )
        data.update(items)
    return data


def extract_fields_from_html(html_content: str, fields: WebpageFields) -> dict[str, Any]:
    tree = html.fromstring(html_content)
    return extract_fields_from_tree(tree, fields)


def extract_items(html_content: str, fields: WebpageFields, root_xpath: str) -> list[dict[str, Any]]:
    items = []
    tree = html.fromstring(html_content)
    for node in tree.xpath(root_xpath):
        data = extract_fields_from_tree(node, fields, select_context_node=True)
        items.append(data)
    return items
