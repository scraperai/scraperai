import time
import unittest
from scraperai import WebdriversManager, SelenoidSettings
from scraperai.llm.chat import OpenAIChatModel
from .settings import SELENOID_URL, selenoid_capabilities, OPEN_AI_TOKEN


class DetectionTests(unittest.TestCase):
    def test_pagination(self):
        from scraperai.parsing.pagination import PaginationDetection

        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=1, capabilities=selenoid_capabilities)
        ])
        driver = webmanager.start_driver()
        chat_model = OpenAIChatModel(api_key=OPEN_AI_TOKEN)
        detector = PaginationDetection(chat_model)
        pagination_test_urls = [
            # 'https://navigator.sk.ru/',
            # 'https://www.mvideo.ru/noutbuki-planshety-komputery-8/noutbuki-118?from=under_search',
            'https://www.ozon.ru/category/smartfony-15502/',
            'https://маркет.промыслы.рф/goods-company/view/30'
        ]
        for url in pagination_test_urls:
            driver.get(url)
            time.sleep(1)
            xpath = detector.find_pagination(driver.page_source)
            self.assertIsNotNone(xpath)


if __name__ == '__main__':
    unittest.main()
