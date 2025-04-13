from abc import ABC, abstractmethod

from src.core.command_context import CommandContext


class Command(ABC):
    @abstractmethod
    def execute(self, context: CommandContext) -> CommandContext:
        pass
