import logging

from src.core import Publisher, Repository
from src.integrations.google.models import GCalendarEvent


class CalendarPublisher(Publisher[GCalendarEvent]):
    def __init__(self, repo: Repository[GCalendarEvent]):
        self.repo = repo

    @property
    def existing_events(self) -> dict[str, GCalendarEvent]:
        return {e.summary: e for e in self.repo.list()}

    def publish(self, event: GCalendarEvent) -> None:
        match = self.existing_events.get(event.summary)

        if not match:
            self.repo.add(event)
            logging.info(f"Created: {event.summary}")
            return

        if match.start.dateTime == event.end.dateTime:
            logging.info(f"Skipped: {event.summary}")
            return

        self.repo.update(match.id, event)
        logging.info(f"Updated: {event.summary}")
