from typing import List

import click

from .cli import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..instance import Instance


@click.option(
    "-s/-S",
    "--show/--no-show",
    help=f"show actual config contents instead",
)
@kiwi_command(
    "list",
    KiwiCommandType.SERVICE,
    short_help="Inspect a kiwi-scp instance",
)
class CMD(KiwiCommand):
    """List projects in this instance, services inside a project or service(s) inside a project"""

    @classmethod
    def run_for_instance(cls, instance: Instance, show: bool = None, **kwargs) -> None:
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
    def run_for_project(cls, instance: Instance, project_name: str, show: bool = None, **kwargs) -> None:
        project = instance.get_project(project_name)

        if project is None:
            KiwiCommand.print_error(f"No project '{project_name}' in kiwi-scp instance at '{instance.directory}'.")
            return

        services = project.get_services()
        if show:
            KiwiCommand.print_header(f"Showing config for all services in project '{project_name}'.")
            click.echo_via_pager(str(services))

        else:
            KiwiCommand.print_header(f"Services in project '{project_name}':")
            KiwiCommand.print_list(service.name for service in services.content)

    @classmethod
    def run_for_services(cls, instance: Instance, project_name: str, service_names: List[str], show: bool = None,
                         **kwargs) -> None:
        project = instance.get_project(project_name)

        if project is None:
            KiwiCommand.print_error(f"No project '{project_name}' in kiwi-scp instance at '{instance.directory}'.")
            return

        services = project.get_services(service_names)
        if show:
            KiwiCommand.print_header(
                f"Showing config for services '{', '.join(service_names)}' in project '{project_name}'.")
            click.echo_via_pager(str(services))

        else:
            KiwiCommand.print_header(f"Matching services in project '{project_name}':")
            KiwiCommand.print_list(service.name for service in services.content)
