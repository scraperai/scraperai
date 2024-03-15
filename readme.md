<p align="center">
  <a href="https://www.medusajs.com">
  <picture>
    <img alt="Medusa logo" height="150px" src="images/logo.png">
    </picture>
  </a>
</p>
<h1 align="center">
  ScraperAI
</h1>
<p align="center">
    ⚡ Scraping has never been easier ⚡
</p>

<h4 align="center">
  <a href="https://docs.scraper-ai.com">Documentation</a> |
  <a href="https://scraper-ai.com">Website</a>
</h4>

## What is ScraperAI

ScrpaerAI is an AI-powered tool that allows users to prepare reciepts ...

### Requirements
- Selenium
- OpenAI
- ...

### Installation

With pip:
```bash
pip install scraperai
```
From source: 
```bash
git clone https://github.com/scraperai/scraperai.git
pip install ./scraperai
```

## Demo

### CLI Application
ScraperAI has a built-in CLI application. Simply run:
```bash
scraperai --url https://www.ycombinator.com/companies
```
or
```bash
scraperai
```
Next, just follow a step-by-step flow. ScraperAI will try to automatically detect page type, pagination, catalog's card and data-fields. At each step, you can check and correct the detection results.

Currently, CLI suppots only `OpenAI` chat model. Therefore you need an openai_api_key to use the app. There are two ways to pass the key.
The first is to add `OPENAI_API_KEY` to your environment or create .env file.
Second option is to pass api key to the script (you will be asked).



Run `scraperai --help` to get help.

### Jupyter notebook


## Usage


# Contributing
Contributions are welcome! Please feel free to open a pull request or an issue.
