import unittest
from .settings import selenoid_capabilities, SELENOID_URL


class WebdriversTests(unittest.TestCase):
    def test_local_driver_connection(self):
        from scraperai import WebdriversManager, SelenoidSettings

        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url='local', max_sessions=5)
        ])
        driver = webmanager.start_driver()
        driver.get('https://apple.com')
        self.assertIsNotNone(driver.page_source)
        webmanager.quit_driver(driver)

    def test_remote_driver_connection(self):
        from scraperai import WebdriversManager, SelenoidSettings

        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=1, capabilities=selenoid_capabilities)
        ])
        driver = webmanager.start_driver()
        driver.get('https://apple.com')
        self.assertIsNotNone(driver.page_source)
        webmanager.quit_driver(driver)


if __name__ == '__main__':
    unittest.main()
