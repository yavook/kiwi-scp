from typing import List

import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project, Services


@click.option(
    "-f/-F",
    "--follow/--no-follow",
    help="output appended data as log grows",
)
@kiwi_command(
    short_help="Show logs",
)
class LogsCommand(KiwiCommand):
    """Show logs of a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], follow: bool = None) -> None:
        # include timestamps
        compose_cmd = ["logs", "-t"]

        # handle following the log output
        if follow:
            compose_cmd.extend(("-f", "--tail=10"))

        compose_cmd.extend(services.names)

        if follow:
            COMPOSE_EXE.run(compose_cmd, **project.process_kwargs)

        else:
            # output is static, use pager
            COMPOSE_EXE.run_with_pager(compose_cmd, **project.process_kwargs)
