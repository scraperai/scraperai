import unittest

from scraperai.crawlers import SeleniumCrawler
from scraperai.lm.openai import OpenAI
from scraperai.parsers.pagination_detector import Pagination, PaginationDetector
from .settings import OPEN_AI_TOKEN, default_webmanager


class DetectionTests(unittest.TestCase):
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
        detector = PaginationDetector(model=OpenAI(OPEN_AI_TOKEN))
        driver = default_webmanager.create_driver()
        crawler = SeleniumCrawler(driver)
        for url, correct_pagination in pagination_tests:
            crawler.get(url)
            test_pagination = detector.find_pagination(crawler.page_source)
            self.assertEqual(correct_pagination.type, test_pagination.type)
            self.assertEqual(correct_pagination.xpath, test_pagination.xpath)
        driver.quit()

    def test_card_detection(self):
        driver = default_webmanager.create_driver()
        crawler = SeleniumCrawler(driver)
        ...
        driver.quit()
        # self.scraper.detect_catalog_item('https://маркет.промыслы.рф/goods-company/view/30')


if __name__ == '__main__':
    unittest.main()
