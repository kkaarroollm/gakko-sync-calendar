import logging
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from bs4 import BeautifulSoup
import time

from google_calendar_manager import TaskEvent


@dataclass
class TaskData:
    href: str
    title: str
    subject: str

    def full_title(self) -> str:
        return f"{self.title} [{self.subject}]"

    def absolute_url(self, base_url: str) -> str:
        return base_url.rstrip("/") + self.href


@dataclass
class GakkoHomeworkScraper:
    username: str
    password: str
    gakko_url: str = "https://gakko.pjwstk.edu.pl/"
    base_url: str = "https://gakko.pjwstk.edu.pl"

    def get_homework(self) -> List[TaskEvent] | None:
        options: Options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")
        # options.binary_location = "/opt/homebrew/bin/chromium"

        driver: WebDriver = webdriver.Chrome(options=options)
        wait: WebDriverWait = WebDriverWait(driver, 20)

        try:
            self._login(driver, wait)
            task_links: List[TaskData] = self._get_task_links(driver)
            events: List[Optional[TaskEvent]] = [
                self._parse_task_detail(driver, task)
                for task in task_links
            ]
            return [e for e in events if e is not None]

        finally:
            driver.quit()

    def _login(self, driver: WebDriver, wait: WebDriverWait) -> None:
        logging.info("Logging in to Gakko")
        driver.get(self.gakko_url)
        wait.until(presence_of_element_located((By.ID, "userNameInput")))
        wait.until(presence_of_element_located((By.ID, "passwordInput")))
        time.sleep(2)

        driver.find_element(By.ID, "passwordInput").send_keys(self.password)
        driver.find_element(By.ID, "userNameInput").send_keys(self.username)

        driver.find_element(By.ID, "submitButton").click()
        WebDriverWait(driver, 15).until(
            presence_of_element_located((By.ID, "tasks_to_do"))
        )
        logging.info("Logged in to Gakko")

    @staticmethod
    def _get_task_links(driver: WebDriver) -> List[TaskData]:
        logging.info("Gathering task links......")
        soup: BeautifulSoup = BeautifulSoup(driver.page_source, "html.parser")

        if not (container := soup.find("div", {"id": "tasks_to_do"})):
            logging.info("Yes siiiir, no more tasks to do here")
            return []

        links: List[TaskData] = []

        for task in container.find_all("a", class_="kt-notification__item"):
            title_div = task.find("div", class_="kt-notification__item-title")
            time_div = task.find("div", class_="kt-notification__item-time")
            href = task.get("href")

            if not (title_div and time_div and href):
                continue

            title: str = title_div.get_text(strip=True)
            subject_info: str = time_div.get_text(strip=True).split("Remaining time")[0].strip()
            links.append(TaskData(href=href, title=title, subject=subject_info))

        return links

    def _parse_task_detail(self, driver: WebDriver, task: TaskData) -> Optional[TaskEvent]:
        full_title: str = task.full_title()
        url: str = task.absolute_url(self.base_url)

        logging.info(f"Ehhh, found task: {full_title}")
        driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(driver.page_source, "html.parser")
        script_tags = soup.find_all("script")
        count_down_date: Optional[int] = None

        pattern = re.compile(r"countDownDate\s*=\s*(\d+);")

        for script in script_tags:
            if not script.string:
                continue

            if match := pattern.search(script.string):
                try:
                    timestamp_ms = int(match.group(1))
                    count_down_date = timestamp_ms // 1000
                    break
                except ValueError as e:
                    logging.error(f"Error parsing timestamp for task: {full_title}: {e}")

        if not count_down_date:
            logging.info(f"Better check Gakko website nooo. No countdown date found for task: {full_title}")

        return TaskEvent(title=full_title, due_date=datetime.fromtimestamp(count_down_date), url=url)
