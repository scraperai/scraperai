# Crawler
Crawler primary goal is to retrieve webpage content. 
Therefore, various web tools can be employed, including as requests, httpx, aiohttp, Selenium, Playwright and others.

However, when facing scraping tasks, additional needs may arise, such as:
- Emulating human interactions (e.g., clicking, scrolling).
- Capturing webpage screenshots.
- Evading anti-scraping measures.

In such cases, automated testing software like Selenium or Playwright is the preferred option. 
We opt for Selenium webdrivers as the default tool due to its convenience, user-friendly nature, and effective techniques for circumventing most website blocks.

## SeleniumCrawler
First, initialize SeleniumCrawler:
```python
from scraperai import SeleniumCrawler

crawler = SeleniumCrawler()
```
By default, it will create a new Chrome webdriver session. You can use any other webdriver by passing it to init:
```python
from scraperai import SeleniumCrawler
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Firefox

your_webdriver = Firefox(service=Service(GeckoDriverManager().install()))
crawler = SeleniumCrawler(driver=your_webdriver)
```

### Selenoid
ScraperAI provides additional tool to work with a pool of selenoids:
```python
from scraperai import SelenoidSettings, WebdriversManager, SeleniumCrawler

# List your Selenoids
selenoids = [
    SelenoidSettings(
        url='selenoid url', 
        max_sessions=10,
        capabilities={
            "browserName": "firefox",
            "browserVersion": "115.0",
            "selenoid:options": {
                "name": "scraperai",
                "enableVideo": False,
                "enableVNC": True,
                "sessionTimeout": '5m'
            },
        }
    ),
]
# Create Webdrivers Manager that will automatically handle sessions and create new drivers
manager = WebdriversManager(selenoids)
# Create new driver
driver = manager.create_driver()
# Create crawler
crawler = SeleniumCrawler(driver)
```

## RequestsCrawler
You can use Requests crawler as follows:
```python
from scraperai import RequestsCrawler

crawler = RequestsCrawler()
```
However, ScraperAI partly relies on rendering functionality (pages screenshots) and interactions (scrolling for "infinite scroll pages" and sometimes clicking for pagination).
Therefore, using `requests` limiting ScraperAI capabilities and may lead to poor results.

## Custom Crawler
To implement a custom crawler, simply inherit from the following abstract class:

```python
import httpx
from scraperai import BaseCrawler
from scraperai.models import Pagination

class YourCrawler(BaseCrawler):
    def __init__(self):
        self.response = None
    
    def get(self, url: str):
        self.response = httpx.get(url)

    @property
    def page_source(self) -> str:
        return self.response
    
    # Optional. Only for automated tests software
    def switch_page(self, pagination: Pagination) -> bool:
        raise NotImplementedError()
```


## Async Crawlers
Async scraping will be introduces in the next versions of the package.