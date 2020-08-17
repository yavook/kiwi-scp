# system
import logging
import os
import subprocess

# parent
from .._constants import KIWI_ROOT

# local
from ._subcommand import SubCommand
from .utils.dockercommand import DockerCommand
from .utils.project import list_projects, get_project_dir
from .utils.rootkit import Rootkit, prefix_path


def _add_prefix(prefix, path):
    abs_path = os.path.abspath(path)
    return os.path.realpath(prefix + '/' + abs_path)


class CopyConfCommand(SubCommand):
    """kiwi copy-conf"""

    def __init__(self):
        super().__init__(
            'copy-conf',
            description="Synchronize all config files to target directory"
        )

    def run(self, runner, config, args):
        conf_dirs = []

        for project_name in list_projects(config):
            project_conf = f"{get_project_dir(config, project_name)}/conf"

            if os.path.isdir(project_conf):
                conf_dirs.append(project_conf)

        if conf_dirs:
            # add target directory
            conf_dirs.append(config['runtime:storage'])
            logging.info(f"Sync directories: {conf_dirs}")

            Rootkit('rsync').run(
                config, args, ['rsync', '-r', *prefix_path(conf_dirs)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        return True
