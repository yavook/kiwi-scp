import click

from .cli import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..config import ProjectConfig
from ..instance import Instance, Services


@click.option(
    "-s/-S",
    "--show/--no-show",
    help=f"EXAMPLE",
)
@kiwi_command(
    "list",
    KiwiCommandType.PROJECT,
    short_help="Inspect a kiwi-scp instance",
)
class CMD(KiwiCommand):
    @classmethod
    def run_for_instance(cls, instance: Instance, show: bool = None, **kwargs):
        print(show)
        print(instance.config.projects)

    @classmethod
    def run_for_services(cls, instance: Instance, project: ProjectConfig, services: Services, show: bool = None,
                         **kwargs):
        print(show)
        print(services)
