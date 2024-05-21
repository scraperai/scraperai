# Examples

## YCombinator scraping
Let's parse companies from [YCombinator](https://www.ycombinator.com/companies/).

### Detection step
First, initialize the the WebCrawler and ParserAI instances:
```python
from scraperai import SeleniumCrawler, ParserAI

crawler = SeleniumCrawler()
parser = ParserAI(openai_api_key='sk-...')
```

Next, open the start page:
```python
start_url = 'https://www.ycombinator.com/companies/'
crawler.get(start_url)
```

We know it's a catalog page, so we'll skip page type detection. Let's detect pagination on the page:
```python
pagination = parser.detect_pagination(crawler.page_source)
## Output: Pagination using infinite scroll
```

Next find catalog's items selector:
```python
catalog_item = parser.detect_catalog_item(page_source=crawler.page_source, website_url=start_url)
## Output: <card_xpath="//a[contains(@class, '_company_99gj3_339')]" url_xpath="//a[contains(@class, '_company_99gj3_339')]/@href">
```

For simplicity, we are not going to details pages in this example. Thus, let's find data fields in the catalog's item card:
```python
fields = parser.extract_fields(html_snippet=catalog_item.html_snippet)
## Output: 4 static fields, 0 dynamic fields
```

Finally, 

### Scraping step

Let's wrap everything from the previous step into a ScraperConfig:
```python
from scraperai.models import ScraperConfig, WebpageType

config = ScraperConfig(
    start_url=start_url,
    page_type=WebpageType.CATALOG,
    pagination=pagination,
    catalog_item=catalog_item,
    open_nested_pages=False,  # We are not going to details pages
    fields=fields,
    max_pages=10,  # Limit pages count
    max_rows=1000  # Limit rows count
)
```

Now, create a Scraper instance. It will help us to collect the data.
```python
from scraperai import Scraper

scraper = Scraper(config=config, crawler=crawler)
```

Finally, iterate over the data using `.scrape()` generator:
```python
items = []
for item in scraper.scrape():
    items.append(item)

print(items)
```

That's all! All the data can be found in `items` list. You may further convert it to any desired format.

## Jupyter notebook
You can find a more detailed example in this [jupyter notebook](https://github.com/scraperai/scraperai/blob/main/examples/ycombinator_full.ipynb).
In the notebook we present two expirements:

1. [List of YCombinator companies](https://www.ycombinator.com/companies/)
2. [List of commits in the repository](https://github.com/scraperai/scraperai/commits/main/)

## Other
Other examples can be found [here](https://github.com/scraperai/scraperai/blob/main/examples/).
