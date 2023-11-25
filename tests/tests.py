import time
import unittest
from scraperai.browser.local import LocalBrowserScraper


class DetectionTests(unittest.TestCase):
    def test_pagination(self):
        from scraperai.parsing.pagination import PaginationDetection

        scraper = LocalBrowserScraper()
        detector = PaginationDetection()
        pagination_test_urls = [
            # 'https://navigator.sk.ru/',
            # 'https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118?from=under_search',
            'https://www.ozon.ru/category/smartfony-15502/',
            'https://маркет.промыслы.рф/goods-company/view/30'
        ]
        for url in pagination_test_urls:
            scraper.get(url)
            time.sleep(1)
            xpath = detector.find_pagination(scraper.page_source)
            self.assertIsNotNone(xpath)


if __name__ == '__main__':
    unittest.main()
