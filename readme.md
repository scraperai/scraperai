<p align="center">
  <picture>
    <img alt="ScraperAI Logo" height="150px" src="images/logo.png">
  </picture>
</p>
<h1 align="center">
  ScraperAI
</h1>
<p align="center">
    ⚡ Scraping has never been easier ⚡
</p>

<!--
<h4 align="center">
  <a href="https://docs.scraper-ai.com">Documentation</a> |
  <a href="https://scraper-ai.com">Website</a>
</h4>
-->

## What is ScraperAI

ScraperAI is an open-source, AI-powered tool designed to simplify web scraping for users of all skill levels. 
By leveraging Large Language Models, such as ChatGPT, ScraperAI extracts data from web pages and generates 
reusable and shareable scraping recipes.

### Features
- Serializable & reusable Scraper Configs
- Automatic data detection
- Automatic XPATHs detection
- Automatic pagination & page type detection
- HTML minification
- ChatGPT support
- Custom LLMs support
- Selenium support
- Custom crawlers support


### Installation

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

### Getting Started

#### Page Type Detector

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

## Demo
### Jupyter notebook
We put example of basic scraper usage in the `example.ipynb`. 
In this notebook we present two expirements:
1. [List of YCombinator companies](https://www.ycombinator.com/companies/)
2. [List of commits in the repository](https://github.com/scraperai/scraperai/commits/main/)


### CLI Application
ScraperAI has a built-in CLI application. Simply run:
```console
scraperai --url https://www.ycombinator.com/companies
```
or simply
```console
scraperai
```

Follow the interactive process as ScraperAI attempts to auto-detect page types, pagination, catalog cards and data fields, 
allowing for manual correction of its detections.
The CLI currently supports only the OpenAI chat model, requiring an `openai_api_key`. 
It can be provided via an environment variable, a `.env` file, or directly to the script.

Use `scraperai --help`  for assistance.

# Roadmap
Our vision for ScraperAI's future includes:
- Add httpx and aiohttp crawlers
- Improve reciepts & prompts
- Release SaaS web app
- Improve prompts
- Add support of different LLMs
- Add [gpt4all](https://github.com/nomic-ai/gpt4all) integration
- Add anti-captcha integration 

We welcome feature requests and ideas from our community.

# Contributing
Your contributions are highly appreciated! Feel free to submit pull requests or issues.
