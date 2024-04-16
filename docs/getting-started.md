# Usage
## Installation
Install ScraperAI easily using pip or from the source.

With pip:
```console
pip install scraperai
```
From source: 
```console
git clone https://github.com/scraperai/scraperai.git
pip install ./scraperai
```

## #### Page Type Detector

Web pages are categorized into four types:

- **Catalog**: Pages with similar repeating elements, such as product lists, articles, companies or table rows.
- **Details**: Pages detailing information about a single product.
- **Captcha**: Captcha pages that hinder scraping efforts. Currently, we do not provide solutions to circumvent captchas.
- **Other**: All other page types not currently supported.

ScraperAI primarily uses page screenshots and the GPT-4 Vision model for page type determination, with a fallback algorithm for cases where screenshots or Vision model access is unavailable. Users can manually set the page type if known.

#### Pagination Detector
This feature is applicable for catalog-type web pages, supporting:

- `xpath`: Xpath of pagination buttons like "Next page", "More", etc.
- `scroll`: Infinite scrolling.
- `url_param`: URL parameter-based pagination (e.g., `website.com/?page=1`).

#### Catalog Item Detector
This feature is specifically designed for catalog-type web pages. It identifies repeating elements that typically 
represent individual data items, such as products, articles, or companies. 
These elements may appear as visually distinct cards or as rows within a table, facilitating the organized display of information.

#### Fields Extractor

The Fields Extractor allows to detect relevant information on the page and then 
find XPATHs that allows to extract this detected information efficiently.
This tool can be used to retrieve information from individual catalog item cards or from nested detailing pages.
We define two types of data fields within HTML page:

- **Static fields:** Fields without explicit names, containing single or multiple values (e.g., product names or prices).
- **Dynamic fields:** Fields with both names and values, typically formatted like table entries.

#### Web Crawler
Our WebCrawler is engineered to:

- Access web pages.
- Simulate human actions (clicking, scrolling).
- Capture screenshots of web pages.

Selenium webdriver is the default tool due to its convenience and ease of use, incorporating techniques to avoid most website blocks. 
Users can implement their versions using other tools like PlayWright. 
The requests package is also supported, albeit with some limitations.

## Examples

You can find all the other examples [here](examples.md).