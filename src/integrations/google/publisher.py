import logging
from dataclasses import dataclass

from src.core import Publisher, Repository
from src.integrations.google.models import GCalendarEvent


@dataclass
class CalendarPublisher(Publisher[GCalendarEvent]):
    repo: Repository[GCalendarEvent]

    def publish(self, event: GCalendarEvent) -> None:
        if not (existing := next((e for e in self.repo.list() if e.summary == event.summary), None)):
            self.repo.add(event)
            logging.info(f"Created: {event.summary}")
            return

        event_with_id = event.model_copy(update={"id": existing.id})
        if event_with_id.is_equal(existing):
            logging.info(f"Skipped: {event.summary}")
            return

        self.repo.update(event_with_id)
        logging.info(f"Updated: {event.summary}")
