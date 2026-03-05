import re
from datetime import datetime
from typing import List

from selenium.webdriver.remote.webdriver import WebDriver

from src.tasks.models import EMPTY_DATE, ScrapedTask

_COUNTDOWN_PATTERN = re.compile(r"countDownDate\s*=\s*(\d+);")


def extract_due_date_via_js(driver: WebDriver) -> datetime:
    try:
        timestamp = driver.execute_script(  # type: ignore[no-untyped-call]
            "return typeof countDownDate !== 'undefined' ? countDownDate : null;"
        )
        if timestamp is not None:
            return datetime.fromtimestamp(int(timestamp) // 1000)
    except Exception:
        pass
    return EMPTY_DATE


def extract_due_date_from_page_source(page_source: str) -> datetime:
    if match := _COUNTDOWN_PATTERN.search(page_source):
        return datetime.fromtimestamp(int(match.group(1)) // 1000)
    return EMPTY_DATE


def extract_due_date(driver: WebDriver) -> datetime:
    due_date = extract_due_date_via_js(driver)
    if due_date != EMPTY_DATE:
        return due_date
    return extract_due_date_from_page_source(driver.page_source)


def enrich_tasks(tasks: List[ScrapedTask], driver: WebDriver, base_url: str) -> List[ScrapedTask]:
    enriched: List[ScrapedTask] = []
    for task in tasks:
        driver.get(task.absolute_url(base_url))
        due_date = extract_due_date(driver)
        if due_date == EMPTY_DATE:
            continue
        enriched.append(task.model_copy(update={"due_date": due_date}))
    return enriched
