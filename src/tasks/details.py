from typing import List
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import re

from src.tasks.models import ScrapedTask, EMPTY_DATE


def extract_due_date_from_html(html: str) -> datetime:
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(r"countDownDate\s*=\s*(\d+);")

    for script in soup.find_all("script"):
        if script.string and (match := pattern.search(script.string)):
            return datetime.fromtimestamp(int(match.group(1)) // 1000)
    return EMPTY_DATE


def enrich_tasks(tasks: List[ScrapedTask], session: requests.Session, base_url: str) -> List[ScrapedTask]:
    # FUTURE: consider using asyncio for parallel requests
    enriched: List[ScrapedTask] = []

    for task in tasks:
        response = session.get(task.absolute_url(base_url))
        due_date = extract_due_date_from_html(response.text)
        if due_date == EMPTY_DATE:
            continue
        enriched.append(task.model_copy(update={"due_date": due_date}))
    return enriched
