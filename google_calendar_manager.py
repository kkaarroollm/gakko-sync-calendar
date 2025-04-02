import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build



@dataclass
class TaskEvent:
    title: str
    due_date: datetime
    url: str

    def to_calendar_format(self) -> dict:
        date_str = self.due_date.date().isoformat()
        return {
            "summary": self.title,
            "start": {"date": date_str},
            "end": {"date": date_str},
            "description": f"Shit to get done: {self.url}",
        }

class GoogleCalendarManager:
    def __init__(self, credentials_path: str = "token.json", calendar_id: str = "primary"):
        self.creds: Credentials = Credentials.from_authorized_user_file(
            credentials_path,
            ["https://www.googleapis.com/auth/calendar"]
        )
        self.service = build("calendar", "v3", credentials=self.creds)
        self.calendar_id = calendar_id

    def _get_existing_events(self) -> dict[str, dict]:
        now = datetime.now(tz=timezone.utc).isoformat()
        events_result = self.service.events().list(
            calendarId=self.calendar_id,
            timeMin=now,
            maxResults=250,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        return {
            e["summary"]: e
            for e in events_result.get("items", [])
            if "summary" in e and "start" in e and "date" in e["start"]
        }

    def post_events(self, events: list[TaskEvent]) -> None:
        """
        Method posts and checks whether an event is already posted
        :param events:
        :return: None
        """
        existing_map = self._get_existing_events()

        for event in events:
            if not (existing := existing_map.get(event.title)):
                self._create_event(event)
                continue

            if existing["start"]["date"] == event.due_date.date().isoformat():
                logging.info(f"Skipping {event.title}")
                continue

            self._update_event(existing["id"], event)
            logging.info(f"Updated {event.title}")

    def _create_event(self, event: TaskEvent) -> None:
        self.service.events().insert(
            calendarId=self.calendar_id,
            body=event.to_calendar_format()
        ).execute()

    def _update_event(self, event_id: str, event: TaskEvent) -> None:
        self.service.events().update(
            calendarId=self.calendar_id,
            eventId=event_id,
            body=event.to_calendar_format()
        ).execute()
        logging.info(f"{event.title}: {event.due_date.isoformat()}")
