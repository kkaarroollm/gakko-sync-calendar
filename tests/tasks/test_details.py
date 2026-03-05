from datetime import datetime
from unittest.mock import MagicMock

from src.tasks.details import enrich_tasks, extract_due_date, extract_due_date_from_page_source, extract_due_date_via_js
from src.tasks.models import EMPTY_DATE, ScrapedTask


def test_extract_due_date_via_js_success():
    driver = MagicMock()
    timestamp = 1700000000000
    driver.execute_script.return_value = timestamp

    result = extract_due_date_via_js(driver)
    assert result == datetime.fromtimestamp(timestamp // 1000)


def test_extract_due_date_via_js_not_found():
    driver = MagicMock()
    driver.execute_script.return_value = None

    result = extract_due_date_via_js(driver)
    assert result == EMPTY_DATE


def test_extract_due_date_from_page_source_valid(render_task_detail_html):
    html, ts = render_task_detail_html()
    result = extract_due_date_from_page_source(html)
    assert result == datetime.fromtimestamp(ts // 1000)


def test_extract_due_date_from_page_source_missing(render_task_detail_html):
    html, _ = render_task_detail_html(include_due_date=False)
    result = extract_due_date_from_page_source(html)
    assert result == EMPTY_DATE


def test_extract_due_date_fallback_to_page_source(render_task_detail_html):
    html, ts = render_task_detail_html()
    driver = MagicMock()
    driver.execute_script.return_value = None
    driver.page_source = html

    result = extract_due_date(driver)
    assert result == datetime.fromtimestamp(ts // 1000)


def test_extract_due_date_prefers_js():
    driver = MagicMock()
    timestamp = 1700000000000
    driver.execute_script.return_value = timestamp

    result = extract_due_date(driver)
    assert result == datetime.fromtimestamp(timestamp // 1000)


def test_enrich_tasks_sets_due_date():
    driver = MagicMock()
    timestamp = 1700000000000
    driver.execute_script.return_value = timestamp

    task = ScrapedTask(href="/task/1", title="T", subject="S")
    enriched = enrich_tasks([task], driver, "https://test.local")

    assert len(enriched) == 1
    assert enriched[0].due_date == datetime.fromtimestamp(timestamp // 1000)
    driver.get.assert_called_once_with("https://test.local/task/1")


def test_enrich_tasks_skips_when_no_due_date():
    driver = MagicMock()
    driver.execute_script.return_value = None
    driver.page_source = "<html>no date here</html>"

    task = ScrapedTask(href="/task/2", title="T", subject="S")
    enriched = enrich_tasks([task], driver, "https://test.local")

    assert enriched == []
