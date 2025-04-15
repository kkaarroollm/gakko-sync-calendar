import pytest

from src.integrations.google.models import GCalendarEvent
from tests.fixtures.factories import ScrapedTaskFactory


def test_list_initially_empty(fake_calendar_repo):
    assert fake_calendar_repo.list() == []


def test_add_event_appears_in_list(fake_calendar_repo):
    event = GCalendarEvent.from_scraped_task(
        task=ScrapedTaskFactory(),
        base_url="https://test.local",
        timezone="Europe/Warsaw",
    )

    fake_calendar_repo.add(event)
    events = fake_calendar_repo.list()

    assert len(events) == 1
    assert events[0].id == event.id
    assert events[0].summary == event.summary


def test_update_event_replaces_existing(fake_calendar_repo):
    task = ScrapedTaskFactory()
    original = GCalendarEvent.from_scraped_task(task, base_url="https://test.local", timezone="Europe/Warsaw")

    fake_calendar_repo.add(original)

    updated = original.model_copy(update={"description": "Changed description"})
    fake_calendar_repo.update(updated)

    events = fake_calendar_repo.list()
    assert len(events) == 1
    assert events[0].id == original.id
    assert events[0].description == updated.description


def test_update_event_raises_if_not_found(fake_calendar_repo):
    task = ScrapedTaskFactory()
    event = GCalendarEvent.from_scraped_task(task, base_url="https://test.local", timezone="Europe/Warsaw")

    with pytest.raises(ValueError, match=event.id):
        fake_calendar_repo.update(event)
