from selenium.webdriver.remote.webelement import WebElement

from .base import BaseWebdriver


def highlight(driver: BaseWebdriver, element: WebElement, color: str, border: int):
    """Highlights (blinks) a Selenium Webdriver element"""

    def apply_style(s):
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, s)

    original_style = element.get_attribute('style')
    apply_style("border: {0}px solid {1};".format(border, color))
