from datetime import datetime, date, time
from typing import Optional, Literal, ClassVar
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field, model_validator

from src.core import GakkoConfig
from src.tasks.models import ScrapedTask

config = GakkoConfig()

class BaseGEventDateTime(BaseModel):
    dateTime: Optional[datetime] = None
    date: Optional[date] = None
    timeZone: Optional[str] = config.default_timezone

    DEFAULT_PARSE_TIME: ClassVar[time]

    @model_validator(mode="before")
    @classmethod
    def parse_google_date(cls, data: dict) -> dict:
        """
        Parses the dateTime or date field from the Google Calendar API response.
        Google Calendar API returns date if the event is all-day, and dateTime if it is not.
        Read more: https://developers.google.com/workspace/calendar/api/v3/reference/events

        :param data: The data dictionary containing the dateTime or date field.
        :return: A dictionary with the parsed dateTime and timeZone.
        """
        raw = data.get("dateTime") or data.get("date")

        if isinstance(raw, datetime):
            dt = raw
        elif isinstance(raw, str):
            if "T" not in raw:
                raw += "T" + cls.DEFAULT_PARSE_TIME.strftime("%H:%M:%S")
            dt = datetime.fromisoformat(raw)
        else:
            raise ValueError(f"Invalid input for dateTime/date: {type(raw)}")

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo(config.default_timezone))

        return {
            "dateTime": dt,
            "timeZone": data.get("timeZone", config.default_timezone)
        }

class GEventStartDateTime(BaseGEventDateTime):
    DEFAULT_PARSE_TIME: ClassVar[time] = time.min  # 00:00:00


class GEventEndDateTime(BaseGEventDateTime):
    DEFAULT_PARSE_TIME: ClassVar[time] = time.max  # 23:59:59


class GReminderOverride(BaseModel):
    method: Literal["email", "popup"]
    minutes: int


class GReminders(BaseModel):
    useDefault: bool = True
    overrides: Optional[list[GReminderOverride]] = Field(default_factory=list)


class GCalendarEvent(BaseModel):
    id: Optional[str] = None
    summary: str
    start: GEventStartDateTime
    end: GEventEndDateTime
    description: str = ""
    reminders: Optional[GReminders]

    @classmethod
    def from_scraped_task(cls, task: "ScrapedTask", *, base_url: str, timezone: str, reminders: Optional[GReminders] = None, description_template: Optional[str] = None ) -> "GCalendarEvent":
        start_date: datetime = datetime.combine(task.due_date, datetime.min.time())
        return cls(
            summary=task.full_title,
            start=GEventStartDateTime(dateTime=start_date, timeZone=timezone),
            end=GEventEndDateTime(dateTime=task.due_date, timeZone=timezone),
            description=description_template.format(task=task) if description_template else f"Shit to get done: {task.absolute_url(base_url=base_url)}",
            reminders=reminders
        )
