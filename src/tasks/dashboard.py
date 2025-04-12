import requests
from bs4 import BeautifulSoup
from src.tasks.models import ScrapedTask

def scrape_tasks_from_dashboard(session: requests.Session, base_url: str) -> list[ScrapedTask]:
    response = session.get( base_url.rstrip("/") + "/dashboard")
    soup = BeautifulSoup(response.text, "html.parser")

    container = soup.find("div", {"id": "tasks_to_do"})
    if not container:
        return []

    tasks = []
    for node in container.find_all("a", class_="kt-notification__item"):
        title = node.find("div", class_="kt-notification__item-title")
        subject = node.find("div", class_="kt-notification__item-time")
        href = node.get("href")

        if not (title and subject and href):
            continue

        tasks.append(ScrapedTask(
            href=href.strip(),
            title=title.get_text(strip=True),
            subject=subject.get_text(strip=True)
        ))

    return tasks