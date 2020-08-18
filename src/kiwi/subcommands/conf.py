# system
import logging
import os
import subprocess

# local
from ._subcommand import SubCommand
from .utils.misc import list_projects, get_project_dir
from .utils.rootkit import Rootkit, prefix_path_mnt

# parent
from .._constants import CONF_DIRECTORY_NAME


class ConfCopyCommand(SubCommand):
    """kiwi conf-copy"""

    def __init__(self):
        super().__init__(
            'conf-copy',
            description="Synchronize all config files to target directory"
        )

    def run(self, runner, config, args):
        conf_dirs = []

        for project_name in list_projects(config):
            project_conf = f"{get_project_dir(config, project_name)}/{CONF_DIRECTORY_NAME}"

            if os.path.isdir(project_conf):
                conf_dirs.append(project_conf)

        if conf_dirs:
            # add target directory
            conf_dirs.append(config['runtime:storage'])
            logging.info(f"Sync directories: {conf_dirs}")

            Rootkit('rsync').run(
                config, args, ['rsync', '-r', *prefix_path_mnt(conf_dirs)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        return True


class ConfPurgeCommand(SubCommand):
    """kiwi conf-purge"""

    def __init__(self):
        super().__init__(
            'conf-purge',
            description="Remove all config files in target directory"
        )

    def run(self, runner, config, args):
        conf_target = f"{config['runtime:storage']}/{CONF_DIRECTORY_NAME}"
        logging.info(f"Purging directories: {conf_target}")

        Rootkit().run(
            config, args, ['rm', '-rf', prefix_path_mnt(conf_target)],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        return True
