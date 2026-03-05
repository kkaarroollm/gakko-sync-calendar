from unittest.mock import MagicMock, patch

from selenium.common.exceptions import TimeoutException

from src.tasks.dashboard import scrape_tasks_from_dashboard
from src.tasks.models import ScrapedTask


def _make_task_element(href: str, title: str, subject: str) -> MagicMock:
    element = MagicMock()
    element.get_attribute.return_value = href

    title_el = MagicMock()
    title_el.text = title

    subject_el = MagicMock()
    subject_el.text = subject

    def _find_element(by, selector):
        if "title" in selector:
            return title_el
        return subject_el

    element.find_element.side_effect = _find_element
    return element


def test_scrape_tasks_valid_elements(mock_driver):
    mock_container = MagicMock()
    task_elements = [
        _make_task_element(f"https://test.local/task/{i}", f"Task {i}", f"Subject {i}")
        for i in range(3)
    ]
    mock_container.find_elements.return_value = task_elements

    with patch("src.tasks.dashboard.WebDriverWait") as mock_wait_cls:
        mock_wait = MagicMock()
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.return_value = mock_container

        tasks = scrape_tasks_from_dashboard(mock_driver, "https://test.local")

    assert isinstance(tasks, list)
    assert len(tasks) == 3
    assert all(isinstance(task, ScrapedTask) for task in tasks)
    for i, task in enumerate(tasks):
        assert task.href == f"/task/{i}"
        assert task.title == f"Task {i}"
        assert task.subject == f"Subject {i}"


def test_scrape_dashboard_no_container(mock_driver):
    with patch("src.tasks.dashboard.WebDriverWait") as mock_wait_cls:
        mock_wait = MagicMock()
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.side_effect = TimeoutException("Timeout")

        tasks = scrape_tasks_from_dashboard(mock_driver, "https://test.local")

    assert tasks == []


def test_scrape_dashboard_no_tasks(mock_driver):
    mock_container = MagicMock()
    mock_container.find_elements.return_value = []

    with patch("src.tasks.dashboard.WebDriverWait") as mock_wait_cls:
        mock_wait = MagicMock()
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.return_value = mock_container

        tasks = scrape_tasks_from_dashboard(mock_driver, "https://test.local")

    assert tasks == []


def test_scrape_skips_incomplete_tasks(mock_driver):
    mock_container = MagicMock()
    complete_el = _make_task_element("https://test.local/task/1", "Task 1", "Subject 1")
    incomplete_el = _make_task_element("", "Task 2", "Subject 2")
    mock_container.find_elements.return_value = [complete_el, incomplete_el]

    with patch("src.tasks.dashboard.WebDriverWait") as mock_wait_cls:
        mock_wait = MagicMock()
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.return_value = mock_container

        tasks = scrape_tasks_from_dashboard(mock_driver, "https://test.local")

    assert len(tasks) == 1
    assert tasks[0].title == "Task 1"
