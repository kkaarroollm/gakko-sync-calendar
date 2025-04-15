from src.core import CommandContext, CommandPipeline
from tests.fixtures.factories import ScrapedTaskFactory
from tests.utils.command_fakes import make_fake_command


def test_add_appends_commands(command_context):
    pipeline = CommandPipeline(command_context)

    cmd = make_fake_command()
    result = pipeline.add(cmd)

    assert cmd in pipeline.commands
    assert result is pipeline


def test_run_executes_commands(command_context):
    pipeline = CommandPipeline(command_context)
    cmd1 = make_fake_command()
    cmd2 = make_fake_command()
    cmd2.last_response = "/response.org"
    pipeline.add(cmd1).add(cmd2)
    result = pipeline.run()
    assert result is command_context


def test_run_executes_commands_in_order(command_context):
    task_1, task_2 = ScrapedTaskFactory.create_batch(2)
    cmd1 = make_fake_command(task=task_1)
    cmd2 = make_fake_command(task=task_2)
    pipeline = CommandPipeline(command_context)
    pipeline.add(cmd1).add(cmd2)
    result = pipeline.run()
    assert result is command_context
    assert len(result.tasks) == 2
    assert result.tasks == [task_1, task_2]


def test_pipeline_executes_side_effect(command_context):
    t = ScrapedTaskFactory.create()

    def _set_client_id(ctx: CommandContext) -> None:
        ctx.config.client_id = "patched"

    cmd = make_fake_command(task=t, side_effect=_set_client_id)

    result = CommandPipeline(command_context).add(cmd).run()

    assert result.tasks == [t]
    assert result.config.client_id == "patched"
