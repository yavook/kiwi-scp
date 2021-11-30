from typing import List

from .cli import KiwiCommand, KiwiCommandType
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance, Project


@kiwi_command(
    cmd_type=KiwiCommandType.SERVICE,
    short_help="Build docker images",
)
class BuildCommand(KiwiCommand):
    """Build images for the whole instance, a project or service(s) inside a project"""

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        COMPOSE_EXE.run(["build", "--pull", *service_names], **project.process_kwargs)
