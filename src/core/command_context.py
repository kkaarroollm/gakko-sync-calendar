from dataclasses import dataclass, field
from typing import List

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.remote.webdriver import WebDriver

from src.core.config import GakkoConfig
from src.tasks.models import ScrapedTask


def _create_driver_from_config(config: GakkoConfig) -> WebDriver:
    options = ChromeOptions()
    if config.chrome_headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    if config.chrome_binary_path:
        options.binary_location = config.chrome_binary_path
    driver = Chrome(options=options)
    driver.implicitly_wait(config.selenium_implicit_wait)
    driver.set_page_load_timeout(config.selenium_page_load_timeout)
    return driver


@dataclass
class CommandContext:
    config: GakkoConfig = field(default_factory=GakkoConfig)
    driver: WebDriver = field(default=None)  # type: ignore[assignment]
    tasks: List[ScrapedTask] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.driver is None:
            self.driver = _create_driver_from_config(self.config)

    @property
    def current_url(self) -> str:
        return self.driver.current_url

    @property
    def page_source(self) -> str:
        return self.driver.page_source

    def quit(self) -> None:
        if self.driver is not None:
            self.driver.quit()
