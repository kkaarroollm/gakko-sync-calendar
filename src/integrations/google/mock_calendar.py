from typing import List

from src.core.protocols import Repository
from src.integrations.google.models import GCalendarEvent


class MockGoogleCalendarRepository(Repository[GCalendarEvent]):
    def __init__(self) -> None:
        self._events: List[GCalendarEvent] = []

    def list(self) -> List[GCalendarEvent]:
        return self._events.copy()

    def add(self, event: GCalendarEvent) -> None:
        self._events.append(event)

    def update(self, event: GCalendarEvent) -> None:
        for i, existing in enumerate(self._events):
            if existing.id == event.id:
                self._events[i] = event
                return
        raise ValueError(f"Event with id {event.id} not found")
