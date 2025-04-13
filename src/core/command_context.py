from dataclasses import dataclass, field
from typing import List, Optional

import requests

from src.core.config import GakkoConfig
from src.tasks.models import ScrapedTask


@dataclass
class CommandContext:
    config: GakkoConfig = field(default_factory=GakkoConfig)
    session: requests.Session = field(default_factory=requests.Session)
    tasks: List[ScrapedTask] = field(default_factory=list)
    _last_response: Optional[requests.Response] = None

    @property
    def last_response(self) -> requests.Response:
        if self._last_response is None:
            raise ValueError("No response available. Ensure a request has been made.")
        return self._last_response

    @last_response.setter
    def last_response(self, response: requests.Response) -> None:
        if not isinstance(response, requests.Response):
            raise ValueError("Expected a 'requests.Response' object.")
        self._last_response = response
