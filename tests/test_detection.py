import unittest

from scraperai.crawlers import SeleniumCrawler, RequestsCrawler
from scraperai.lm.openai import OpenAI, JsonOpenAI
from scraperai.parsers import CatalogItemDetector
from scraperai.parsers.pagination_detector import Pagination, PaginationDetector
from .settings import OPENAI_API_KEY, default_webmanager


class TestDetection(unittest.TestCase):
    def test_pagination(self):
        pagination_tests = [
            (
                'https://ai-scraper.com/',
                Pagination(type='scroll')
            ),
            (
                'https://маркет.промыслы.рф/goods-company/view/30',
                Pagination(type='xpath', xpath="//*[@class='ajax-pagination-more']")
            ),
            # ('https://www.ozon.ru/category/smartfony-15502/', False),
        ]
        detector = PaginationDetector(model=OpenAI(OPENAI_API_KEY))
        driver = default_webmanager.create_driver()
        crawler = SeleniumCrawler(driver)
        for url, correct_pagination in pagination_tests:
            crawler.get(url)
            test_pagination = detector.find_pagination(crawler.page_source)
            self.assertEqual(correct_pagination.type, test_pagination.type)
            self.assertEqual(correct_pagination.xpath, test_pagination.xpath)
        driver.quit()

    def test_card_detection(self):
        crawler = RequestsCrawler()
        url = 'https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods-company/view/27'
        crawler.get(url)
        detector = CatalogItemDetector(model=JsonOpenAI(OPENAI_API_KEY))
        item = detector.detect_catalog_item(crawler.page_source)
        print(item)


if __name__ == '__main__':
    unittest.main()
