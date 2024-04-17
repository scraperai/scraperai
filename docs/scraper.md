# Scraper

Use `Scraper` class to collect data from webpages. Start by initializing `Scraper` instance:

```python
from scraperai import Scraper, SeleniumCrawler
from scraperai.models import ScraperConfig

config = ScraperConfig(...)  # Assume you have already have a ScraperConfig
crawler = SeleniumCrawler()

scraper = Scraper(config=config, crawler=crawler)
```

Now you are ready to iterate over the data using `.scrape()` generator:
```python
items = []
for item in scraper.scrape():
    items.append(item)

print(items)
```

Afterwards transform the data in any desired format:
```python
import pandas as pd

df = pd.DataFrame(items)
df.to_csv('data.csv')
df.to_excel('data.xlsx')
```