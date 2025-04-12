from typing import List

from src.core import Command, CommandContext


class CommandPipeline:
    def __init__(self, context: CommandContext):
        self.context = context
        self.commands: List[Command] = []

    def add(self, command: Command) -> "CommandPipeline":
        self.commands.append(command)
        return self

    def run(self) -> CommandContext:
        for command in self.commands:
            self.context = command.execute(self.context)
        return self.context


