import os
import shutil

import click

from .cmd import KiwiCommandType, KiwiCommand
from .decorators import kiwi_command
from .._constants import DEFAULT_DOCKER_COMPOSE_NAME, COMPOSE_FILE_NAME, RESERVED_PROJECT_NAMES
from ..config import ProjectConfig
from ..instance import Instance
from ..project import Project


@kiwi_command()
class NewCommand(KiwiCommand):
    """Create new empty project(s) in this instance"""

    type = KiwiCommandType.PROJECTS

    @classmethod
    def run_for_project(cls, instance: Instance, project: Project, **kwargs) -> None:
        KiwiCommand.print_error(f"Project {project.name} already exists!")

    @classmethod
    def run_for_new_project(cls, instance: Instance, project_name: str, **kwargs) -> None:
        if project_name in RESERVED_PROJECT_NAMES:
            KiwiCommand.print_error(f"Project name '{project_name}' is reserved!")
            return

        try:
            os.mkdir(project_name)
            instance.config.projects.append(ProjectConfig(
                name=project_name,
                enabled=False,
            ))
            shutil.copy(
                DEFAULT_DOCKER_COMPOSE_NAME,
                instance.directory.joinpath(project_name).joinpath(COMPOSE_FILE_NAME)
            )
            instance.save_config(instance.config)

        except FileExistsError:
            KiwiCommand.print_error(f"Project directory {project_name} already exists!")
