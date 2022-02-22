from typing import List

import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance
from ..project import Project
from ..services import Services


@kiwi_command(
    short_help="Pull docker images",
)
class PullCommand(KiwiCommand):
    """Pull images for the whole instance, a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_filtered_services(cls, instance: Instance, project: Project, services: Services,
                                  new_service_names: List[str], **kwargs) -> None:
        if not services:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Pull images for the entire project {project.name} instead?",
                    default=True
            ):
                return

        COMPOSE_EXE.run(["pull", "--ignore-pull-failures", *services.names], **project.process_kwargs)
