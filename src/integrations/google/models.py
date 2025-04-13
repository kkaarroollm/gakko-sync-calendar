from datetime import date, datetime, time
from typing import ClassVar, Literal, Optional
from zoneinfo import ZoneInfo

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.core import gakko_config
from src.tasks.models import ScrapedTask


class AliasSerializableBaseModel(BaseModel):
    """Base model for alias serialization."""

    model_config = ConfigDict(serialize_by_alias=True)


class BaseGEventDateTime(AliasSerializableBaseModel):
    date_time: Optional[datetime] = Field(alias="dateTime")
    date: Optional[date] = None
    time_zone: Optional[str] = Field(alias="timeZone", default=gakko_config.default_timezone)

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
            dt = dt.replace(tzinfo=ZoneInfo(gakko_config.default_timezone))

        return {"dateTime": dt, "timeZone": data.get("timeZone", gakko_config.default_timezone)}


class GEventStartDateTime(BaseGEventDateTime):
    DEFAULT_PARSE_TIME: ClassVar[time] = time.min  # 00:00:00


class GEventEndDateTime(BaseGEventDateTime):
    DEFAULT_PARSE_TIME: ClassVar[time] = time.max  # 23:59:59


class GReminderOverride(BaseModel):
    method: Literal["email", "popup"]
    minutes: int


class GReminders(AliasSerializableBaseModel):
    use_default: bool = Field(default=True, alias="useDefault")
    overrides: list[GReminderOverride] = Field(default_factory=list)


class GCalendarEvent(BaseModel):
    id: Optional[str] = None
    summary: str
    start: GEventStartDateTime
    end: GEventEndDateTime
    description: str = ""
    reminders: Optional[GReminders]

    require_id: bool = Field(default=False, exclude=True, description="Flag for ID requirement")

    @model_validator(mode="after")
    def check_id(self) -> "GCalendarEvent":
        if self.require_id and self.id is None:
            raise ValueError(f"Missing ID for event: {self.summary}")
        return self

    def is_equal(self, other: "GCalendarEvent") -> bool:
        """Check if two GCalendarEvent instances are equal based on their start and end times."""
        return (
            self.start.date_time == other.start.date_time
            and self.end.date_time == other.end.date_time
            and self.summary == other.summary
        )

    @classmethod
    def from_scraped_task(
        cls,
        task: "ScrapedTask",
        *,
        base_url: str,
        timezone: str,
        reminders: Optional[GReminders] = None,
        description_template: Optional[str] = None,
    ) -> "GCalendarEvent":
        start_date: datetime = datetime.combine(task.due_date, datetime.min.time())
        return cls(
            summary=task.full_title,
            start=GEventStartDateTime(dateTime=start_date, timeZone=timezone),
            end=GEventEndDateTime(dateTime=task.due_date, timeZone=timezone),
            description=description_template.format(task=task)
            if description_template
            else f"Shit to get done: {task.absolute_url(base_url=base_url)}",
            reminders=reminders,
        )

    @classmethod
    def from_google_api(cls, data: dict) -> "GCalendarEvent":
        return cls(**data, require_id=True)
