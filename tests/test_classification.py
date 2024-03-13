import unittest
from scraperai.parsers import WebpageType, WebpageVisionClassifier
from scraperai.crawlers import SeleniumCrawler
from scraperai.utils.image import compress_b64_image
from scraperai.vision.openai import VisionOpenAI
from .settings import default_webmanager, OPENAI_API_KEY


class TestClassification(unittest.TestCase):
    def test_classification(self):
        driver = default_webmanager.create_driver()
        crawler = SeleniumCrawler(driver)
        classifier = WebpageVisionClassifier(model=VisionOpenAI(OPENAI_API_KEY))
        test_urls = [
            ('https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/market/craft/1', WebpageType.CATALOG),
            ('https://xn--80akogvo.xn--k1abfdfi3ec.xn--p1ai/goods/view/287096', WebpageType.DETAILS),
            ('https://ai-scraper.com/', WebpageType.OTHER),
        ]
        for url, page_type in test_urls:
            crawler.get(url)
            screenshot = crawler.get_screenshot_as_base64()
            screenshot = compress_b64_image(screenshot, aspect_ratio=0.5)
            test_page_type = classifier.classify(screenshot)
            self.assertEqual(page_type, test_page_type)
        driver.quit()


if __name__ == '__main__':
    unittest.main()
