import click

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from .._constants import KIWI_CONF_NAME
from ..instance import Instance, Project


@click.option(
    "-f/-F",
    "--force/--no-force",
    help=f"skip confirmation",
)
@kiwi_command(
    cmd_type=KiwiCommandType.PROJECT,
)
class DisableCommand(KiwiCommand):
    """Disable a project"""

    @classmethod
    def run_for_instance(cls, instance: Instance, force: bool = None) -> None:
        if not force:
            if not KiwiCommand.danger_confirm("This will disable all projects in this instance."):
                return

        super().run_for_instance(instance)

    @classmethod
    def run_for_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        if not project.project_config.enabled:
            KiwiCommand.print_error(f"Project {project.name} is already disabled!")
            return

        project.project_config.enabled = False
        KiwiCommand.print_header(f"Project {project.name} disabled")

        # write out the new kiwi.yml
        with open(instance.directory.joinpath(KIWI_CONF_NAME), "w") as file:
            instance.config.dump_kiwi_yml(file)