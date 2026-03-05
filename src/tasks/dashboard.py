from urllib.parse import urlparse

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait

from src.tasks.models import ScrapedTask


def scrape_tasks_from_dashboard(driver: WebDriver, base_url: str) -> list[ScrapedTask]:
    driver.get(base_url.rstrip("/") + "/dashboard")

    try:
        container = WebDriverWait(driver, 10).until(
            expected_conditions.presence_of_element_located((By.ID, "tasks_to_do"))
        )
    except TimeoutException:
        return []

    task_elements = container.find_elements(By.CSS_SELECTOR, "a.kt-notification__item")

    tasks: list[ScrapedTask] = []
    for element in task_elements:
        try:
            href = element.get_attribute("href")
            title_el = element.find_element(By.CSS_SELECTOR, "div.kt-notification__item-title")
            subject_el = element.find_element(By.CSS_SELECTOR, "div.kt-notification__item-time")

            title = title_el.text.strip()
            subject = subject_el.text.strip()

            if not (href and title and subject):
                continue

            path = urlparse(href).path
            tasks.append(ScrapedTask(href=path, title=title, subject=subject))
        except Exception:
            continue

    return tasks
