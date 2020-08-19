# system
import logging
import os
import shutil

# local
from .utils.project import Projects
from ._subcommand import ProjectCommand

# parent
from .._constants import DEFAULT_DOCKER_COMPOSE_NAME


class NewCommand(ProjectCommand):
    """kiwi new"""

    def __init__(self):
        super().__init__(
            'new', num_projects='+',
            description="Create new empty project(s) in this instance"
        )

    def run(self, runner, config, args):
        result = True
        projects = Projects.from_args(args)

        for project in projects:
            if project.exists():
                logging.error(f"Project '{project.get_name()}' exists in this instance!")
                result = False

            else:
                logging.info(f"Creating project '{project.get_name()}'")
                os.mkdir(project.enabled_dir_name())
                shutil.copy(DEFAULT_DOCKER_COMPOSE_NAME, project.compose_file_name())

        return result
