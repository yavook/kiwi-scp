# system
import logging
import os
import shutil

# local
from .utils.misc import get_project_names, get_project_dir, get_project_down_dir
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

        for project_name in get_project_names(args):
            project_dir = get_project_dir(config, project_name)
            project_down_dir = get_project_down_dir(config, project_name)

            if os.path.isdir(project_dir) or os.path.isdir(project_down_dir):
                logging.error(f"Project '{project_name}' exists in this instance!")
                result = False

            else:
                logging.info(f"Creating project '{project_name}'")
                os.mkdir(project_dir)
                shutil.copy(DEFAULT_DOCKER_COMPOSE_NAME, os.path.join(project_dir, "docker-compose.yml"))

        return result
