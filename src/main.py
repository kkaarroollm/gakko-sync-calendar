import logging
import os

from src.auth.command import AuthorizeCommand, SubmitFormCommand, SubmitLoginCommand
from src.core import CalendarConfig, CommandContext, CommandPipeline, Publisher, gakko_config
from src.integrations.google.calendar_repository import GoogleCalendarRepository
from src.integrations.google.models import GCalendarEvent
from src.integrations.google.publisher import CalendarPublisher
from src.tasks.commands import FetchTaskDetailsCommand, ScrapeTasksFromDashboardCommand


def main() -> None:
    ctx = CommandContext(config=gakko_config)
    pipeline = CommandPipeline(ctx)

    (
        pipeline.add(AuthorizeCommand())
        .add(SubmitLoginCommand())
        .add(SubmitFormCommand())
        .add(SubmitFormCommand())
        .add(ScrapeTasksFromDashboardCommand())
        .add(FetchTaskDetailsCommand())
    )

    ctx = pipeline.run()

    repo = GoogleCalendarRepository(config=CalendarConfig())
    publisher: Publisher = CalendarPublisher(repo=repo)

    for task in ctx.tasks:
        event = GCalendarEvent.from_scraped_task(
            task=task, base_url=str(gakko_config.base_url), timezone="Europe/Warsaw"
        )
        publisher.publish(event)


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",  # noqa
        handlers=[logging.FileHandler("logs/sync.log"), logging.StreamHandler()],
    )

    main()
