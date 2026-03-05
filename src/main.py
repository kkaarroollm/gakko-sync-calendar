import logging
import os
from datetime import datetime

from src.auth.command import NavigateToLoginCommand, SubmitCredentialsCommand
from src.core import CalendarConfig, CommandContext, CommandPipeline, Publisher, gakko_config
from src.integrations.google.calendar_repository import GoogleCalendarRepository
from src.integrations.google.models import GCalendarEvent
from src.integrations.google.publisher import CalendarPublisher
from src.tasks.commands import FetchTaskDetailsCommand, ScrapeTasksFromDashboardCommand


def main() -> None:
    ctx = CommandContext(config=gakko_config)

    try:
        pipeline = CommandPipeline(ctx)

        (
            pipeline.add(NavigateToLoginCommand())
            .add(SubmitCredentialsCommand())
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
    finally:
        ctx.quit()


if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",  # noqa
        handlers=[logging.FileHandler(f"logs/sync_{datetime.now().strftime('%Y-%m-%d')}.log"), logging.StreamHandler()],
    )

    main()
