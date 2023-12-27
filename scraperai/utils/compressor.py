import htmlmin
import requests
from bs4 import BeautifulSoup
import logging


logger = logging.getLogger(__file__)

BAD_TAGS = {
    'script', 'style', 'meta', 'noscript', 'footer', 'header'
}
GOOD_ATTRS = {
    'class', "id", "name", 'href', 'text',
}


# Function to remove tags
def compress_html(html, good_attrs: set = None,
                  bad_tags: set = None,
                  use_substituions: bool = True) -> tuple[str, dict[str, str]]:
    if good_attrs is None:
        good_attrs = GOOD_ATTRS
    if bad_tags is None:
        bad_tags = BAD_TAGS

    # Remove spaces and new lines
    html = htmlmin.minify(str(BeautifulSoup(html, "html.parser")), remove_empty_space=True)
    logger.info(f'Initial HTML length: {len(html)}')
    # Remove bad tags
    soup = BeautifulSoup(html, "html.parser")
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
    for tag in soup.find_all():
        if tag.text.strip() == '':
            tag.extract()
    logger.info(f'Final html length: {len(str(soup))}')
    return str(soup), substituions


def test():
    url = 'https://re-store.ru/apple-iphone/'
    html = requests.get(url).content.decode('utf-8')
    with open('../research/files/test/compressed.html', 'w+') as f:
        f.write(html)

    # req


if __name__ == '__main__':
    test()
