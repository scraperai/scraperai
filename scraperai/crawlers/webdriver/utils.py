import logging

from selenium.common import JavascriptException
from selenium.webdriver.remote.webdriver import WebDriver


logger = logging.getLogger('scraperai')


def highlight_by_xpath(driver: WebDriver, xpath: str, color: str, border: int):
    xpath = xpath.replace('"', '\'')
    script = f"""
var result = document.evaluate("{xpath}", document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
for (var i = 0; i < result.snapshotLength; i++) {{
    var element = result.snapshotItem(i);
    if (element.style) {{
        element.style.border = '{border}px solid {color}';
    }}
}}"""
    try:
        driver.execute_script(script)
    except JavascriptException as e:
        logger.exception(e)
