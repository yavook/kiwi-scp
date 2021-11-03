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
    def run_for_instance(cls, instance: Instance, show: bool = None, **kwargs):
        if show:
            click.secho(f"Showing config for kiwi-scp instance at '{instance.directory}'.", fg="green", bold=True)
            click.echo_via_pager(instance.config.kiwi_yml)

        else:
            click.secho(f"Projects in kiwi-scp instance at '{instance.directory}':", fg="green", bold=True)

            for project in instance.config.projects:
                click.echo(
                    click.style("  - ", fg="green") +
                    click.style(project.name, fg="blue") +
                    click.style(' (disabled)' if not project.enabled else '', fg="red")
                )

    @classmethod
    def run_for_services(cls, instance: Instance, project_name: str, services: List[str], show: bool = None,
                         **kwargs):
        print(show)
        print(services)
