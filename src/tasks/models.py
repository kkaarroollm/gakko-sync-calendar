from datetime import datetime
from typing import Annotated

from pydantic import constr, BaseModel

HrefStr = Annotated[str, constr(strip_whitespace=True, pattern=r"^/.*")]
EMPTY_DATE = datetime.min

class ScrapedTask(BaseModel):
    href: HrefStr
    title: str
    subject: str
    due_date: datetime = EMPTY_DATE

    @property
    def full_title(self) -> str:
        return f"{self.title} [{self.subject}]"

    def absolute_url(self, base_url: str) -> str:
        return base_url.rstrip("/") + self.href

