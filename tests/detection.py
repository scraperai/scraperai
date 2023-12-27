import time
import unittest
from scraperai import WebdriversManager, SelenoidSettings
from scraperai.scraping import ScraperAI
from .settings import SELENOID_URL, selenoid_capabilities, OPEN_AI_TOKEN


class DetectionTests(unittest.TestCase):
    def __init__(self, method: str = 'runTest'):
        super().__init__(method)

        self.webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url='local', max_sessions=48, capabilities=selenoid_capabilities)
        ])
        self.scraper = ScraperAI(api_key=OPEN_AI_TOKEN, webmanager=self.webmanager)

    def test_pagination(self):
        pagination_tests = [
            # ('https://ai-scraper.com/', True),
            ('https://маркет.промыслы.рф/goods-company/view/30', False),
            # ('https://www.ozon.ru/category/smartfony-15502/', False),
        ]
        for url, is_none in pagination_tests:
            xpath = self.scraper.detect_pagination(url)
            print(f"XPATH IS '{xpath}'")
            try:
                self.assertEqual(xpath is None, is_none)
            except Exception as e:
                self.scraper.quit_driver()
                raise e

    def test_card_detection(self):
        self.scraper.detect_catalog_item('https://маркет.промыслы.рф/goods-company/view/30')
        time.sleep(20)
        self.scraper.quit_driver()


if __name__ == '__main__':
    unittest.main()
