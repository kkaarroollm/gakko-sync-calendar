import logging

from src.integrations.google.models import GCalendarEvent
from src.integrations.google.publisher import CalendarPublisher
from tests.fixtures.factories import ScrapedTaskFactory


def test_publish_adds_if_event_not_exists(fake_calendar_repo, caplog):
    task = ScrapedTaskFactory()
    event = GCalendarEvent.from_scraped_task(task, base_url="https://test.local", timezone="Europe/Warsaw")

    publisher = CalendarPublisher(repo=fake_calendar_repo)

    with caplog.at_level(logging.INFO):
        publisher.publish(event)

    events = fake_calendar_repo.list()
    assert len(events) == 1
    assert events[0].summary == event.summary
    assert "Created" in caplog.text


def test_publish_skips_if_event_is_equal(fake_calendar_repo, caplog):
    task = ScrapedTaskFactory()
    event = GCalendarEvent.from_scraped_task(task, base_url="https://test.local", timezone="Europe/Warsaw")

    fake_calendar_repo.add(event)
    publisher = CalendarPublisher(repo=fake_calendar_repo)

    with caplog.at_level(logging.INFO):
        publisher.publish(event)

    events = fake_calendar_repo.list()
    assert len(events) == 1
    assert "Skipped" in caplog.text


def test_publish_updates_if_event_differs(fake_calendar_repo, caplog):
    task = ScrapedTaskFactory()
    original = GCalendarEvent.from_scraped_task(task, base_url="https://test.local", timezone="Europe/Warsaw")
    fake_calendar_repo.add(original)

    modified = original.model_copy(update={"description": "Updated!"})
    publisher = CalendarPublisher(repo=fake_calendar_repo)

    with caplog.at_level(logging.INFO):
        publisher.publish(modified)

    events = fake_calendar_repo.list()
    assert len(events) == 1
    assert events[0].description == modified.description
    assert "Updated" in caplog.text
