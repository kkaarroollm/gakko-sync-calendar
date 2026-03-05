import time
from pathlib import Path
from unittest.mock import MagicMock

import faker
import pytest
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
def mock_driver():
    driver = MagicMock()
    driver.current_url = "https://test.local"
    driver.page_source = "<html></html>"
    return driver


@pytest.fixture
def command_context(mock_config, mock_driver):
    return CommandContext(config=mock_config, driver=mock_driver)


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
