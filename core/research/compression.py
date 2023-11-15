import json

import requests
from tqdm import tqdm

from bs4 import BeautifulSoup
import htmlmin

import pandas as pd
from concurrent.futures import ThreadPoolExecutor


BAD_TAGS = {
    'script', 'style', 'meta', 'noscript', 'button'
}
BAD_ATTRIBUTES = {
    'class', "id", "name", "style", 'meta', 'href',
    'lang', 'language', 'onmouseover', 'onmouseout', 'script', 'font',
    'dir', 'face', 'size', 'color', 'width', 'height', 'hspace',
    'border', 'valign', 'align', 'background', 'bgcolor', 'text', 'link', 'vlink',
    'alink', 'cellpadding', 'cellspacing'
}


# Function to remove tags
def compress_html(html):
    # Remove spaces and new lines
    html = htmlmin.minify(html, remove_empty_space=True)

    # Remove bad tags
    soup = BeautifulSoup(html, "html.parser")
    for tag in BAD_TAGS:
        [x.extract() for x in soup.find_all(tag)]

    # Remove bad attributes
    all_attrs = BAD_ATTRIBUTES
    for tag in soup():
        for attr in tag.attrs:
            all_attrs.add(attr)

    for tag in soup():
        for attribute in all_attrs:
            del tag[attribute]

    # Substitute texts
    index = 0
    substituions = []
    for p in soup.find_all('p') + soup.find_all('cite'):
        _id = str(index)
        substituions.append(p.string)
        p.string = _id
        index += 1

    # Remove empty tags
    for tag in soup.find_all():
        if tag.text.strip() == '':
            tag.extract()
    with open('files/test/full_wiki_compressed.html', 'w+') as f:
        f.write(str(soup))
    return str(soup)


headers = {
    'sec-ch-ua': '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36',
    'sec-ch-ua-platform': '"macOS"',
}


def fetch(url: str) -> list | None:
    try:
        response = requests.get(url, headers=headers, timeout=120)
        if response.status_code != 200:
            return None
        html = response.content.decode('utf-8')
        if len(html) == 0:
            return None
        compressed_html = compress_html(html)
        return [len(html), len(compressed_html)]
    except Exception as e:
        return None


def collect_statistics(urls: list[str]):
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(tqdm(
            executor.map(fetch, urls),
            total=len(urls),
            bar_format="{desc:<5}{percentage:3.0f}%|{bar}{r_bar}",
            ncols=50
        ))
        results = [x for x in results if x]
    return results


def main():
    df = pd.read_csv('top-1m.csv', header=None)
    urls = ['https://' + x for x in df[1].values.tolist()]
    urls = urls[0:10000]
    data = collect_statistics(urls)
    with open('output.json', 'w+') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    main()
