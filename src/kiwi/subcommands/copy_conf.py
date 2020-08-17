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
        logging.info("Building image kiwi-config/auxiliary:rsync")
        DockerCommand('docker').run(
            config, args,
            [
                'build',
                '-t', 'kiwi-config/auxiliary:rsync',
                '-f', f"{KIWI_ROOT}/images/rsync.Dockerfile",
                f"{KIWI_ROOT}/images"
            ],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        conf_sources = []

        for project_name in list_projects(config):
            project_conf = f"{get_project_dir(config, project_name)}/conf"

            if os.path.isdir(project_conf):
                conf_sources.append(project_conf)

        if conf_sources:
            print(f"Syncing {conf_sources} to '{config['runtime:storage']}'")
            conf_sources = [f"'{_add_prefix('/mnt', src)}'" for src in conf_sources]
            conf_sources = ' '.join(conf_sources)

            conf_target = f"'{_add_prefix('/mnt', config['runtime:storage'])}'"
            logging.debug(f"Config sources {conf_sources}, Config target {conf_target}")

            DockerCommand('docker').run(
                config, args,
                [
                    'run', '--rm',
                    '-v', '/:/mnt',
                    '-u', 'root',
                    'kiwi-config/auxiliary:rsync',
                    'ash', '-c', f"rsync -r {conf_sources} {conf_target}"
                ],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

        return True
