from datetime import datetime

from src.tasks.details import enrich_tasks, extract_due_date_from_html
from src.tasks.models import EMPTY_DATE, ScrapedTask


def test_extract_due_date_valid(render_task_detail_html):
    html, ts = render_task_detail_html()
    result = extract_due_date_from_html(html)

    assert result == datetime.fromtimestamp(ts // 1000)


def test_extract_due_date_missing_due_date(render_task_detail_html):
    html, _ = render_task_detail_html(include_due_date=False)
    result = extract_due_date_from_html(html)

    assert result == EMPTY_DATE


def test_extract_due_date_missing_script(render_task_detail_html):
    html, _ = render_task_detail_html(include_script=False)
    result = extract_due_date_from_html(html)

    assert result == EMPTY_DATE


def test_enrich_tasks_sets_due_date(render_task_detail_html, mock_session):
    html, ts = render_task_detail_html()
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    task = ScrapedTask(href="/task/1", title="T", subject="S")
    enriched = enrich_tasks([task], mock_session, "https://test.local")

    assert len(enriched) == 1
    assert enriched[0].due_date == datetime.fromtimestamp(ts // 1000)


def test_enrich_tasks_skips_when_no_due_date(render_task_detail_html, mock_session):
    html, _ = render_task_detail_html(include_due_date=False)
    mock_session.get.return_value.status_code = 200
    mock_session.get.return_value.text = html

    task = ScrapedTask(href="/task/2", title="T", subject="S")
    enriched = enrich_tasks([task], mock_session, "https://test.local")

    assert enriched == []


def test_extract_due_date_skips_script_without_string():
    html = '<html><body><script src="some.js"></script></body></html>'
    result = extract_due_date_from_html(html)
    assert result == EMPTY_DATE
