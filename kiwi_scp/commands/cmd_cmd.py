from typing import Tuple

import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project


@click.argument(
    "compose_args",
    metavar="[ARG]...",
    nargs=-1,
)
@click.argument(
    "compose_cmd",
    metavar="COMMAND",
)
@kiwi_command(
    cmd_type=KiwiCommandType.PROJECT,
    short_help="Run docker-compose command",
    # ignore arguments looking like options
    # just pass everything down to docker-compose
    context_settings={"ignore_unknown_options": True},
)
class CmdCommand(KiwiCommand):
    """Run raw docker-compose command in a project"""

    @classmethod
    def run_for_existing_project(cls, instance: Instance, project: Project, compose_cmd: str = None,
                                 compose_args: Tuple[str] = None) -> None:
        if project.project_config.enabled:
            COMPOSE_EXE.run([compose_cmd, *compose_args], **project.process_kwargs)
