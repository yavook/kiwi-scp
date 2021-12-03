from typing import List

import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance
from ..project import Project
from ..services import Services


@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"skip confirmation",
)
@kiwi_command(
    short_help="Restart kiwi services",
)
class RestartCommand(KiwiCommand):
    """Restart the whole instance, a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_instance(cls, instance: Instance, force: bool = None) -> None:
        if not force:
            if not KiwiCommand.danger_confirm(
                    "This will restart the entire instance.",
            ):
                return

        super().run_for_instance(instance)

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        if not services:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Restart the entire project {project.name} instead?",
                    default=True
            ):
                return

        COMPOSE_EXE.run(["restart", *services.names], **project.process_kwargs)
