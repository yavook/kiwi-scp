from typing import List

import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance
from ..project import Project
from ..services import Services


@kiwi_command(short_help="Bring up kiwi services")
class UpCommand(KiwiCommand):
    """Bring up the whole instance, a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        if not services:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Bring up the entire project {project.name} instead?",
                    default=True
            ):
                return

        instance.create_net()
        services.copy_configs()

        COMPOSE_EXE.run(["up", "-d", *services.names], **project.process_kwargs)
