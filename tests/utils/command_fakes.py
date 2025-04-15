from typing import Any, Callable, Optional

from src.core import Command, CommandContext
from src.tasks.models import ScrapedTask


def make_fake_command(
    task: Optional[ScrapedTask] = None, side_effect: Optional[Callable[[CommandContext], None]] = None, **context_updates: Any
) -> Command:
    class FakeCommand(Command):
        def execute(self, context: CommandContext) -> CommandContext:
            if side_effect:
                side_effect(context)

            for key, value in context_updates.items():
                if hasattr(context, key):
                    setattr(context, key, value)

            if task:
                context.tasks.append(task)

            return context

    return FakeCommand()
