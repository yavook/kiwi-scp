from typing import List

import click

from .cli import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..instance import Instance, Project


@click.option(
    "-s/-S",
    "--show/--no-show",
    help=f"show actual config contents instead",
)
@kiwi_command(
    cmd_type=KiwiCommandType.SERVICE,
    short_help="Inspect a kiwi-scp instance",
)
class ListCommand(KiwiCommand):
    """List projects in this instance, services inside a project or service(s) inside a project"""

    @classmethod
    def run_for_instance(cls, instance: Instance, show: bool = None) -> None:
        if show:
            KiwiCommand.print_header(f"Showing config for kiwi-scp instance at '{instance.directory}'.")
            click.echo_via_pager(instance.config.kiwi_yml)

        else:
            KiwiCommand.print_header(f"Projects in kiwi-scp instance at '{instance.directory}':")
            KiwiCommand.print_list(
                project.name + click.style(" (disabled)" if not project.enabled else "", fg="red")
                for project in instance.config.projects
            )

    @classmethod
    def run_for_project(cls, instance: Instance, project: Project, show: bool = None) -> None:
        if show:
            KiwiCommand.print_header(f"Showing config for all services in project '{project.name}'.")
            click.echo_via_pager(str(project.services))

        else:
            KiwiCommand.print_header(f"Services in project '{project.name}':")
            KiwiCommand.print_list(service.name for service in project.services.content)

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], show: bool = None) -> None:
        services = project.services.filter_existing(service_names)
        if show:
            service_names = [service.name for service in services.content]
            KiwiCommand.print_header(
                f"Showing config for matching services '{', '.join(service_names)}' in project '{project.name}'.")
            click.echo_via_pager(str(services))

        else:
            KiwiCommand.print_header(f"Matching services in project '{project.name}':")
            KiwiCommand.print_list(service.name for service in services.content)
