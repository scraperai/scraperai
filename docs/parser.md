# ParserAI

ParserAI is a key component that helps to analyze the webpage, detect type, pagination, catalog item and data-fields.

Start by initializing ParserAI instance:
```python
from scraperai import ParserAI

# Using OpenAI
parser = ParserAI(openai_api_key='sk-...')

# Using Custom Models
parser = ParserAI(
    json_lm_model=YourJsonLM(),
    vision_model=YourVisionLM(),  # Optional
)
```

## Detecting page type

Web pages are categorized into four types:

- **Catalog**: Pages with similar repeating elements, such as product lists, articles, companies or table rows.
- **Details**: Pages detailing information about a single product.
- **Captcha**: Captcha pages that hinder scraping efforts. Currently, we do not provide solutions to circumvent captchas.
- **Other**: All other page types not currently supported.

ScraperAI primarily uses page screenshots and the GPT-4 Vision model for page type determination, with a fallback algorithm for cases where screenshots or Vision model access is unavailable.

```python
from scraperai import ParserAI, SeleniumCrawler

# Open the page
start_url = 'https://www.ycombinator.com/companies'
crawler = SeleniumCrawler()
crawler.get(start_url)

parser = ParserAI(openai_api_key='sk-...')

page_type = parser.detect_page_type(
    page_source=crawler.page_source, 
    screenshot=crawler.get_screenshot_as_base64()  # Optional
)
```

## Detecting pagination
This feature is applicable for catalog-type web pages, supporting:

- `xpath`: Xpath of pagination buttons like "Next page", "More", etc.
- `scroll`: Infinite scrolling.
- `urls`: a list of URLs.

```python
from scraperai import ParserAI, SeleniumCrawler

# Open the page
start_url = 'https://www.ycombinator.com/companies'
crawler = SeleniumCrawler()
crawler.get(start_url)

parser = ParserAI(openai_api_key='sk-...')

pagination = parser.detect_pagination(crawler.page_source)
```

## Detecting catalog item
This feature is specifically designed for catalog-type web pages. 
It identifies repeating elements that typically represent individual data items, such as products, articles, or companies. 
These elements may appear as visually distinct cards or as rows within a table, facilitating the organized display of information.

```python
from scraperai import ParserAI, SeleniumCrawler

# Open the page
start_url = 'https://www.ycombinator.com/companies'
crawler = SeleniumCrawler()
crawler.get(start_url)

parser = ParserAI(openai_api_key='sk-...')

catalog_item = parser.detect_catalog_item(crawler.page_source, start_url)
print(catalog_item.url_xpath)
print(catalog_item.card_xpath)
```

## Detecting data fields
The Fields Extractor allows to detect relevant information on the page and then 
find XPATHs that allows to extract this detected information efficiently.
This tool can be used to retrieve information from individual catalog item cards or from nested detailing pages.
We define two types of data fields within HTML page:

- **Static fields:** Fields without explicit names, containing single or multiple values (e.g., product names or prices).
- **Dynamic fields:** Fields with both names and values, typically formatted like table entries.

```python
fields = parser.extract_fields(catalog_item.html_snippet)
print(fields.static_fields)
print(fields.dynamic_fields)
```

## Combine everything together
After you have finished the detection process combine all data together in a ScraperConfig to pass it to a Scraper:

```python
from scraperai.models import ScraperConfig

config = ScraperConfig(
    start_url=start_url,
    page_type=page_type,
    pagination=pagination,
    catalog_item=catalog_item,
    open_nested_pages=True,
    fields=fields,
    max_pages=10,
    max_rows=1000
)
```
