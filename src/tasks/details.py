import re
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup, Tag

from src.tasks.models import EMPTY_DATE, ScrapedTask


def extract_due_date_from_html(html: str) -> datetime:
    soup = BeautifulSoup(html, "html.parser")
    pattern = re.compile(r"countDownDate\s*=\s*(\d+);")

    for script in soup.find_all("script"):
        if not (isinstance(script, Tag) and script.string):
            continue
        if match := pattern.search(script.string):
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
