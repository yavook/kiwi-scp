# system
import logging
import os

# local
from .utils.misc import get_project_names, get_project_dir, get_project_down_dir
from ._subcommand import ProjectCommand


class EnableCommand(ProjectCommand):
    """kiwi enable"""

    def __init__(self):
        super().__init__(
            'enable', num_projects='+',
            description="Enable whole project(s) in this instance"
        )

    def run(self, runner, config, args):
        result = True

        for project_name in get_project_names(args):
            project_dir = get_project_dir(config, project_name)
            project_down_dir = get_project_down_dir(config, project_name)

            if os.path.isdir(project_down_dir):
                logging.info(f"Enabling project '{project_name}'")
                os.rename(project_down_dir, project_dir)

            elif os.path.isdir(project_dir):
                logging.warning(f"Project '{project_name}' is already enabled!")
                result = False

            else:
                logging.warning(f"Project '{project_name}' not found in instance!")
                result = False

        return result
