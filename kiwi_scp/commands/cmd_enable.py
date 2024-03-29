import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from .._constants import KIWI_CONF_NAME
from ..instance import Instance
from ..project import Project


@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"skip confirmation",
)
@kiwi_command()
class EnableCommand(KiwiCommand):
    """Enable project(s)"""

    type = KiwiCommandType.PROJECTS

    @classmethod
    def run_for_instance(cls, instance: Instance, force: bool = None) -> None:
        if not force:
            if not KiwiCommand.danger_confirm("This will enable all projects in this instance."):
                return

        super().run_for_instance(instance)

    @classmethod
    def run_for_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        if project.config.enabled:
            KiwiCommand.print_error(f"Project {project.name} is already enabled!")
            return

        project.config.enabled = True
        KiwiCommand.print_header(f"Project {project.name} enabled")

        # write out the new kiwi.yml
        with open(instance.directory.joinpath(KIWI_CONF_NAME), "w") as file:
            instance.config.dump_kiwi_yml(file)
