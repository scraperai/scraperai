import logging
from typing import Any

import htmlmin
import tiktoken
from bs4 import BeautifulSoup
from lxml import html, etree

from pydantic import BaseModel
from tiktoken import Encoding

logger = logging.getLogger(__file__)

BAD_TAGS = {
    'script', 'style', 'meta', 'noscript', 'footer', 'header'
}
GOOD_ATTRS = {
    'class', 'id', 'name', 'href', 'text', 'src'
}


def minify_html(html_content: str,
                good_attrs: set[str] = None,
                bad_tags: set[str] = None,
                use_substituions: bool = True,
                remove_empty_tags: bool = False) -> tuple[str, dict[str, str]]:
    if good_attrs is None:
        good_attrs = GOOD_ATTRS
    if bad_tags is None:
        bad_tags = BAD_TAGS

    # Remove spaces and new lines
    html_content = htmlmin.minify(str(BeautifulSoup(html_content, "html.parser")), remove_empty_space=True)
    logger.info(f'Initial HTML length: {len(html_content)}')
    # Remove bad tags
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in bad_tags:
        [x.extract() for x in soup.find_all(tag)]
    # Remove bad attributes
    all_attrs = set()
    for tag in soup():
        for attr in tag.attrs:
            all_attrs.add(attr)
    bad_attrs = all_attrs.difference(good_attrs)
    for tag in soup():
        for attribute in bad_attrs:
            del tag[attribute]
    # Substitute texts
    index = 0
    substituions = {}
    if use_substituions:
        for p in soup.find_all('p') + soup.find_all('cite'):
            if len(str(p.string)) > 100:
                _id = f'my_text_{index}'
                substituions[_id] = str(p.string)
                p.string = _id
                index += 1
    # Remove empty tags
    if remove_empty_tags:
        for tag in soup.find_all():
            if tag.text.strip() == '':
                tag.extract()
    logger.info(f'Final html length: {len(str(soup))}')
    return str(soup), substituions


def get_pretty_html_text(node: BeautifulSoup) -> str:
    t = node.text.strip()
    while '\n\n' in t:
        t = t.replace("\n\n", "\n")
    return t


class HtmlPart(BaseModel):
    xpath: str
    html_size: int
    text_size: int
    html_content: str
    text_content: str

    def __str__(self) -> str:
        return f"(xpath='{self.xpath}' html_size='{self.html_size}' text_size='{self.text_size}')"

    def __repr__(self) -> str:
        return self.__str__()


def split_html(html_content: str, *,
               max_html_size: int = None,
               max_text_size: int = None,
               encoding: Encoding = None) -> list[HtmlPart]:
    if encoding is None:
        encoding = tiktoken.encoding_for_model('gpt-4-0125-preview')
    if max_html_size is not None and max_text_size is not None:
        raise ValueError('One of max_html_size, max_text_size should be None')
    elif max_text_size is None and max_text_size is None:
        raise ValueError('One of max_html_size, max_text_size should not be None')
    max_target_size = max_html_size or max_text_size or 0

    def get_text_size(text: str) -> int:
        return len(encoding.encode(text))

    tree = html.fromstring(html_content)
    pieces = []

    def traverse(node):
        content = etree.tostring(node, pretty_print=False, method="html", encoding='unicode')
        soup = BeautifulSoup(content, 'html.parser')
        text = get_pretty_html_text(soup)
        html_size = get_text_size(content)
        text_size = get_text_size(text)
        current_piece_size = html_size if max_html_size else text_size
        if current_piece_size <= 3:
            pass
        elif current_piece_size <= max_target_size:
            pieces.append(HtmlPart(
                xpath=node.getroottree().getpath(node),
                html_size=html_size,
                text_size=text_size,
                html_content=content,
                text_content=text
            ))
        else:
            for child in node.getchildren():
                traverse(child)

    traverse(tree)
    return pieces


def remove_nodes_by_xpath(html_content: str, xpaths: list[str]) -> str:
    """
    Remove nodes from an HTML document based on a list of xpaths.

    Args:
        html_content (str): The HTML content as a string.
        xpaths (list): A list of xpath strings identifying the nodes to remove.

    Returns:
        str: The modified HTML content as a string, with the specified nodes removed.
    """
    # Parse the HTML
    tree = html.fromstring(html_content)

    # Iterate over the list of xpaths and remove each matching node
    parents_children = []
    for xpath in xpaths:
        for node in tree.xpath(xpath):
            parents_children.append((node.getparent(), node))
    for parent, child in parents_children:
        parent.remove(child)
    # Return the modified HTML as a string
    html_content = etree.tostring(tree, pretty_print=False, method="html", encoding='unicode')
    return html_content


def get_node_text(node) -> str:
    if isinstance(node, str):
        text = node
    else:
        text = etree.tostring(node, method="text", encoding='unicode')
    text = text.strip()
    return text


def extract_field_by_xpath(tree, xpath: str) -> Any:
    nodes = tree.xpath(xpath)
    nodes = [get_node_text(node) for node in nodes]
    if len(nodes) == 0:
        value = None
    elif len(nodes) == 1:
        value = nodes[0]
    else:
        value = nodes
    return value


def extract_dynamic_fields_by_xpath(labels_xpath: str,
                                    values_xpath: str,
                                    *,
                                    html_content: str = None,
                                    tree=None) -> dict[str, str]:
    if html_content:
        tree = html.fromstring(html_content)
    elif tree is None:
        raise ValueError('One of `html_content` or `tree` should not be None')
    labels = list(tree.xpath(labels_xpath))
    values = list(tree.xpath(values_xpath))
    if len(labels) != len(values):
        raise ValueError(f'Labels and values are of different size: {len(labels)} != {len(values)}')
    return {get_node_text(key).strip(): get_node_text(value).strip() for key, value in zip(labels, values)}

