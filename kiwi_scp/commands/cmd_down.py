from typing import List

import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project


@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"skip confirmation",
)
@kiwi_command(
    cmd_type=KiwiCommandType.SERVICE,
    short_help="Bring down kiwi services",
)
class DownCommand(KiwiCommand):
    """Bring down the whole instance, a project or service(s) inside a project"""

    @classmethod
    def run_for_instance(cls, instance: Instance, force: bool = None) -> None:
        if not force:
            if not KiwiCommand.danger_confirm(
                    "This will bring down the entire instance.",
                    "",
                    "This may not be what you intended, because:",
                    " - Bringing down the instance stops ALL services in here",
            ):
                return

        super().run_for_instance(instance)

        # TODO net-down

    @classmethod
    def run_for_existing_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        COMPOSE_EXE.run(["down"], **project.process_kwargs)

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        services = project.services.filter_existing(service_names)
        existing_service_names = [
            service.name
            for service in services.content
        ]
        all_service_names_exist = len(existing_service_names) == len(service_names)

        if not existing_service_names and not all_service_names_exist:
            if not click.confirm(
                    "Did not find any of those services. \n"
                    f"Bring down the entire project {project.name} instead?",
                    default=True
            ):
                return

        COMPOSE_EXE.run(["stop", *existing_service_names], **project.process_kwargs)
        COMPOSE_EXE.run(["rm", "-f", *existing_service_names], **project.process_kwargs)
