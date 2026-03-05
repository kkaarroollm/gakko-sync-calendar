from unittest.mock import patch

import pytest

from src.core import CommandContext
from src.core.exceptions import CommandPipelineError
from src.tasks.commands import FetchTaskDetailsCommand, ScrapeTasksFromDashboardCommand
from src.tasks.models import EMPTY_DATE
from tests.fixtures.factories import ScrapedTaskFactory


def test_scrape_tasks_command_raises_on_empty(mock_driver, mock_config):
    context = CommandContext(config=mock_config, driver=mock_driver)

    with patch("src.tasks.commands.scrape_tasks_from_dashboard", return_value=[]):
        command = ScrapeTasksFromDashboardCommand()
        with pytest.raises(CommandPipelineError, match=command.NO_TASKS_FOUND):
            command.execute(context)


def test_scrape_tasks_command_success(mock_driver, mock_config):
    tasks = ScrapedTaskFactory.build_batch(3)
    context = CommandContext(config=mock_config, driver=mock_driver)

    with patch("src.tasks.commands.scrape_tasks_from_dashboard", return_value=tasks):
        command = ScrapeTasksFromDashboardCommand()
        result = command.execute(context)

    assert len(result.tasks) == 3
    assert result.tasks[0].href == tasks[0].href


def test_fetch_task_details_success(mock_driver, mock_config):
    task = ScrapedTaskFactory()
    assert task.due_date == EMPTY_DATE

    enriched_task = task.model_copy(update={"due_date": "2025-01-01T00:00:00"})
    context = CommandContext(config=mock_config, driver=mock_driver, tasks=[task])

    with patch("src.tasks.commands.enrich_tasks", return_value=[enriched_task]):
        command = FetchTaskDetailsCommand()
        result = command.execute(context)

    assert len(result.tasks) == 1
    assert result.tasks[0].due_date != EMPTY_DATE
