from src.core import Command, CommandContext
from src.core.exceptions import CommandPipelineError
from src.tasks.dashboard import scrape_tasks_from_dashboard
from src.tasks.details import enrich_tasks


class ScrapeTasksFromDashboardCommand(Command):
    NO_TASKS_FOUND: str = "No tasks found on the dashboard."

    def execute(self, context: CommandContext) -> CommandContext:
        tasks = scrape_tasks_from_dashboard(session=context.session, base_url=str(context.config.base_url))
        if not tasks:
            raise CommandPipelineError(self.NO_TASKS_FOUND)

        context.tasks = tasks
        return context


class FetchTaskDetailsCommand(Command):
    def execute(self, context: CommandContext) -> CommandContext:
        context.tasks = enrich_tasks(
            tasks=context.tasks, session=context.session, base_url=str(context.config.base_url)
        )
        return context
