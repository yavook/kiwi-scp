from typing import List

import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project, Services


@kiwi_command(
    cmd_type=KiwiCommandType.SERVICE,
    short_help="Bring up kiwi services",
)
class UpCommand(KiwiCommand):
    """Bring up the whole instance, a project or service(s) inside a project"""

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        # TODO conf-copy
        # TODO net-up

        if not services:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Bring up the entire project {project.name} instead?",
                    default=True
            ):
                return

        COMPOSE_EXE.run(["up", "-d", *services.names], **project.process_kwargs)
