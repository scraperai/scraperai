import unittest

from scraperai import WebdriversManager, SelenoidSettings
from scraperai.webdriver.manager import TooManySessions
from .settings import selenoid_capabilities, SELENOID_URL


class WebdriversTests(unittest.TestCase):
    test_url = 'https://apple.com'
    test_substr = '<link rel="canonical" href="https://www.apple.com/">'

    def test_local_driver_connection(self):
        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url='local', max_sessions=5)
        ])
        driver = webmanager.create_driver()
        driver.get(self.test_url)
        self.assertTrue(self.test_substr in driver.page_source)
        driver.quit()

    def test_remote_driver_connection(self):
        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=1, capabilities=selenoid_capabilities)
        ])
        driver = webmanager.create_driver()
        driver.get(self.test_url)
        self.assertTrue(self.test_substr in driver.page_source)
        driver.quit()

    def test_remote_driver_limits(self):
        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=1, capabilities=selenoid_capabilities)
        ])
        driver = webmanager.create_driver()
        driver.get(self.test_url)
        self.assertTrue(self.test_substr in driver.page_source)
        flag = False
        try:
            webmanager.create_driver()
        except TooManySessions:
            flag = True
        self.assertTrue(flag)
        driver.quit()
        self.assertEqual(webmanager.local_sessions, 0)

    def test_remote_driver_recreation(self):
        webmanager = WebdriversManager(selenoids=[
            SelenoidSettings(url=SELENOID_URL, max_sessions=2, capabilities=selenoid_capabilities)
        ])
        driver = webmanager.create_driver()
        driver.get(self.test_url)
        driver_url = driver.url
        driver_session_id = driver.get_session_id()

        driver = webmanager.from_session_id(driver_url, driver_session_id)
        self.assertTrue(self.test_substr in driver.page_source)
        driver.quit()


if __name__ == '__main__':
    unittest.main()
