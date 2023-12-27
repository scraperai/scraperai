import unittest
from scraperai import WebdriversManager, SelenoidSettings
from scraperai.parsing.classifier import WebpageType
from scraperai.scraping import ScraperAI
from .settings import SELENOID_URL, selenoid_capabilities, OPEN_AI_TOKEN


class ClassificationTests(unittest.TestCase):
    def test_classification(self):
        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=50, capabilities=selenoid_capabilities)
        ])
        scraper = ScraperAI(api_key=OPEN_AI_TOKEN, webmanager=webmanager)

        test_urls = [
            ('https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/market/craft/1', WebpageType.CATALOG),
            ('https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/287096', WebpageType.DETAILS),
            ('https://ai-scraper.com/', WebpageType.OTHER),
        ]
        for url, page_type in test_urls:
            test_page_type = scraper.detect_page_type(url)
            self.assertEqual(page_type, test_page_type)
        scraper.quit_driver()


if __name__ == '__main__':
    unittest.main()
