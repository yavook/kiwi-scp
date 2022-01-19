from typing import List

import click
from click import get_current_context

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..instance import Instance
from ..project import Project
from ..services import Services


@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"skip confirmation",
)
@kiwi_command(
    short_help="Update kiwi services",
)
class UpdateCommand(KiwiCommand):
    """Update the whole instance, a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        if not services:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Update the entire project {project.name} instead?",
                    default=True
            ):
                return

        from .cmd_build import BuildCommand
        from .cmd_down import DownCommand
        from .cmd_pull import PullCommand
        from .cmd_up import UpCommand

        ctx = get_current_context()
        ctx.forward(BuildCommand)
        ctx.forward(PullCommand)
        # TODO conf-copy
        ctx.forward(DownCommand)
        ctx.forward(UpCommand)
