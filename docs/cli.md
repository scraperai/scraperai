# CLI Application
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
