from src.tasks.dashboard import scrape_tasks_from_dashboard
from src.tasks.models import ScrapedTask


def test_scrape_tasks_valid_html(render_dashboard_html, mock_session):
    html, expected_tasks = render_dashboard_html(task_count=3)

    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    tasks = scrape_tasks_from_dashboard(mock_session, "https://test.local")

    assert isinstance(tasks, list)
    assert len(tasks) == 3
    assert all(isinstance(task, ScrapedTask) for task in tasks)

    for i in range(3):
        assert tasks[i].href == expected_tasks[i].href
        assert tasks[i].title == expected_tasks[i].title
        assert tasks[i].subject == expected_tasks[i].subject


def test_scrape_dashboard_no_tasks(render_dashboard_html, mock_session):
    html, _ = render_dashboard_html(task_count=0)
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    tasks = scrape_tasks_from_dashboard(mock_session, "https://test.local")

    assert tasks == []


def test_scrape_dashboard_invalid_html(mock_session):
    html = "<html><body><div>No task container here</div></body></html>"

    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    tasks = scrape_tasks_from_dashboard(mock_session, "https://test.local")

    assert tasks == []


def test_scrape_skips_incomplete_tasks(render_dashboard_html, mock_session):
    html, expected_tasks = render_dashboard_html(task_count=3)
    html = html.replace('href="', "", 1)

    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    tasks = scrape_tasks_from_dashboard(mock_session, "https://test.local")

    assert len(tasks) == 2
    assert all(task.title != "Incomplete Task" for task in tasks)
