from typing import List

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from ..executable import COMPOSE_EXE
from ..instance import Instance
from ..project import Project


@kiwi_command(
    short_help="Build docker images",
)
class BuildCommand(KiwiCommand):
    """Build images for the whole instance, a project or service(s) inside a project"""

    type = KiwiCommandType.SERVICES
    enabled_only = True

    @classmethod
    def run_for_services(cls, instance: Instance, project: Project, service_names: List[str], **kwargs) -> None:
        COMPOSE_EXE.run(["build", "--pull", *service_names], **project.process_kwargs)
