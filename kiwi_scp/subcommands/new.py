# system
import logging
import os
import shutil

# local
from .._constants import DEFAULT_DOCKER_COMPOSE_NAME
from ..subcommand import ProjectCommand


class NewCommand(ProjectCommand):
    """kiwi new"""

    def __init__(self):
        super().__init__(
            'new', num_projects='+',
            action="Creating",
            description="Create new empty project(s) in this instance"
        )

    def _run_project(self, runner, args, project):
        if project.exists():
            logging.error(f"Project '{project.get_name()}' exists in this instance!")
            return False

        else:
            os.mkdir(project.disabled_dir_name())
            shutil.copy(DEFAULT_DOCKER_COMPOSE_NAME, project.compose_file_name())
            logging.debug(f"Project '{project.get_name()}' created")
            return True
