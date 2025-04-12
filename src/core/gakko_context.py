from dataclasses import dataclass, field
import requests
from src.core import GakkoConfig
from src.tasks.models import ScrapedTask
from typing import List


@dataclass
class CommandContext:
    config: GakkoConfig = field(default_factory=GakkoConfig)
    session: requests.Session = field(default_factory=requests.Session)
    last_response: requests.Response = None
    tasks: List[ScrapedTask] = field(default_factory=list)
