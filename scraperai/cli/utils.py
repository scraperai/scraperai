import os
import re

import appdirs

from scraperai.models import WebpageFields


DATA_DIR = appdirs.user_data_dir(appname='scraperai', appauthor='scraperai')
os.makedirs(DATA_DIR, exist_ok=True)


def convert_ranges_to_indices(input_str: str) -> set[int]:
    """

    :param input_str: range string e.g. "1-5, 3,4,5"
    :return:
    """
    result = set()
    input_str = input_str.replace(' ', '')
    if not re.match(r'[0-9,-]+', input_str):
        raise ValueError('Not a valid range')
    elements = input_str.split(',')
    for element in elements:
        if '-' in element:
            start, end = element.split('-')
            result.update(range(int(start), int(end) + 1))
        else:
            result.add(int(element))
    return result


def delete_field_by_name(fields: WebpageFields, field_name_to_delete: str) -> bool:
    deleted = False
    for i in range(len(fields.static_fields)):
        if fields.static_fields[i].field_name == field_name_to_delete:
            del fields.static_fields[i]
            deleted = True
            break
    for i in range(len(fields.dynamic_fields)):
        if fields.dynamic_fields[i].section_name == field_name_to_delete:
            del fields.dynamic_fields[i]
            deleted = True
            break
    return deleted


def delete_fields_by_range(fields: WebpageFields, range_to_delete: set[int]) -> bool:
    deleted = False
    offset_index = len(fields.static_fields)

    indices_to_remove = list(range_to_delete)
    indices_to_remove.sort(reverse=True)
    for index in indices_to_remove:
        if 0 <= index < len(fields.static_fields):
            fields.static_fields.pop(index)
            deleted = True

    for index in indices_to_remove:
        if 0 <= index - offset_index < len(fields.dynamic_fields):
            fields.dynamic_fields.pop(index - offset_index)
            deleted = True
    return deleted


def validate_url(url: str) -> bool:
    pattern = re.compile(r'^https?://(?:www\.)?[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(?:/.*)?$')
    return bool(pattern.match(url))
