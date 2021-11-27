from typing import List

import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project


@kiwi_command(
    cmd_type=KiwiCommandType.SERVICE,
    short_help="Bring up kiwi services",
)
class UpCommand(KiwiCommand):
    """Bring up the whole instance, a project or service(s) inside a project"""

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        # TODO conf-copy
        # TODO net-up

        services = project.services.filter_existing(service_names)
        existing_service_names = [
            service.name
            for service in services.content
        ]
        all_service_names_exist = len(existing_service_names) == len(service_names)

        if not existing_service_names and not all_service_names_exist:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Bring up the entire project {project.name} instead?",
                    default=True
            ):
                return

        COMPOSE_EXE.run(["up", "-d", *existing_service_names], **project.process_kwargs)
