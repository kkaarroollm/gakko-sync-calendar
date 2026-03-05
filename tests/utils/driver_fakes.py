from unittest.mock import MagicMock

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def make_mock_driver(
    url: str = "https://fake.local",
    page_source: str = "<html></html>",
) -> MagicMock:
    driver = MagicMock(spec=WebDriver)
    driver.current_url = url
    driver.page_source = page_source
    driver.execute_script = MagicMock(return_value=None)
    return driver


def make_mock_element(
    text: str = "",
    href: str = "",
    tag_name: str = "div",
) -> MagicMock:
    element = MagicMock(spec=WebElement)
    element.text = text
    element.tag_name = tag_name
    element.get_attribute = MagicMock(return_value=href)
    return element
