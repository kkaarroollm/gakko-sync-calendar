import pytest

from src.core import CommandContext
from src.core.exceptions import CommandPipelineError
from src.tasks.commands import FetchTaskDetailsCommand, ScrapeTasksFromDashboardCommand
from src.tasks.models import EMPTY_DATE
from tests.fixtures.factories import ScrapedTaskFactory


def test_scrape_tasks_command_raises_on_empty(render_dashboard_html, mock_session, mock_config):
    html, _ = render_dashboard_html(task_count=0)
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    context = CommandContext(config=mock_config, session=mock_session)

    command = ScrapeTasksFromDashboardCommand()

    with pytest.raises(CommandPipelineError, match=command.NO_TASKS_FOUND):
        command.execute(context)


def test_scrape_tasks_command_success(render_dashboard_html, mock_session, mock_config):
    html, expected_tasks = render_dashboard_html(task_count=3)
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    context = CommandContext(config=mock_config, session=mock_session)

    command = ScrapeTasksFromDashboardCommand()
    result = command.execute(context)

    assert len(result.tasks) == 3
    assert result.tasks[0].href == expected_tasks[0].href


def test_fetch_task_details_success(render_task_detail_html, mock_session, mock_config):
    html, ts = render_task_detail_html()
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    task = ScrapedTaskFactory()
    assert task.due_date == EMPTY_DATE

    context = CommandContext(config=mock_config, session=mock_session, tasks=[task])

    command = FetchTaskDetailsCommand()
    result = command.execute(context)

    assert len(result.tasks) == 1
    assert result.tasks[0].due_date.timestamp() == ts // 1000
