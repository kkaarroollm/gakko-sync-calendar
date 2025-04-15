import time
from pathlib import Path
from unittest.mock import Mock

import faker
import pytest
import requests
from jinja2 import Environment, FileSystemLoader
from pydantic import HttpUrl

from src.core import CommandContext, GakkoConfig
from src.integrations.google.mock_calendar import MockGoogleCalendarRepository
from src.tasks.models import ScrapedTask
from tests.fixtures.factories import ScrapedTaskFactory

TEMPLATE_DIR = Path(__file__).parent / "fixtures" / "html"
env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


@pytest.fixture
def mock_config():
    return GakkoConfig(base_url=HttpUrl("https://test.local"), client_id=faker.Faker().uuid4())


@pytest.fixture
def fake_calendar_repo():
    return MockGoogleCalendarRepository()


@pytest.fixture
def command_context(mock_config, mock_session):
    return CommandContext(config=mock_config, session=mock_session)


@pytest.fixture
def mock_session():
    return Mock(spec=requests.Session)


@pytest.fixture
def render_dashboard_html():
    def _generate(task_count: int = 1) -> tuple[str, list[ScrapedTask]]:
        template = env.get_template("dashboard_template.html")
        tasks = ScrapedTaskFactory.build_batch(task_count)
        html = template.render(tasks=tasks)
        return html, tasks

    return _generate


@pytest.fixture
def render_task_detail_html():
    def _generate(include_due_date=True, include_script=True, timestamp=None):
        template = env.get_template("task_detail_template.html")
        ts = timestamp or int(time.time() * 1000)
        html = template.render(
            include_script=include_script,
            include_due_date=include_due_date,
            timestamp=ts,
        )
        return html, ts if include_due_date else None

    return _generate
