from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from src.core import CalendarConfig, gakko_config
from src.integrations.google.models import GCalendarEvent
from src.core.protocols import Repository


@dataclass
class GoogleCalendarRepository(Repository[GCalendarEvent]):
    config: CalendarConfig
    _creds: Credentials = field(init=False, repr=False)
    _service: Any = field(init=False, repr=False)
    _calendar_id: str = field(init=False)

    def __post_init__(self):
        self._creds = Credentials.from_authorized_user_file(
            self.config.credentials_path,
            ["https://www.googleapis.com/auth/calendar"]
        )
        self._service = build("calendar", "v3", credentials=self._creds)
        self._calendar_id = self.config.calendar_id

    def list(self) -> list[GCalendarEvent]:
        response = self._service.events().list(
            calendarId=self._calendar_id,
            timeMin=datetime.now(ZoneInfo(gakko_config.default_timezone)).isoformat(),
            maxResults=250,
            singleEvents=True,
            orderBy="startTime"
        ).execute()


        raw_items = response.get("items", [])
        return [GCalendarEvent(**item) for item in raw_items]

    def add(self, event: GCalendarEvent) -> None:
        self._service.events().insert(
            calendarId=self._calendar_id,
            body=event.model_dump(mode="json")
        ).execute()

    def update(self, event_id: str, event: GCalendarEvent) -> None:
        self._service.events().update(
            calendarId=self._calendar_id,
            eventId=event_id,
            body=event.model_dump(mode="json")
        ).execute()