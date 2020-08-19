# system
import logging
import subprocess

# local
from .._constants import CONF_DIRECTORY_NAME
from ..subcommand import SubCommand
from ..config import LoadedConfig
from ..projects import Projects
from ..rootkit import Rootkit, prefix_path_mnt


class ConfCopyCommand(SubCommand):
    """kiwi conf-copy"""

    def __init__(self):
        super().__init__(
            'conf-copy',
            action="Syncing all configs for",
            description="Synchronize all config files to target directory"
        )

    def _run_instance(self, runner, args):
        conf_dirs = [
            project.conf_dir_name()
            for project in Projects.from_dir().filter_enabled()
        ]

        if conf_dirs:
            # add target directory
            conf_dirs.append(LoadedConfig.get()['runtime:storage'])
            logging.info(f"Sync directories: {conf_dirs}")

            Rootkit('rsync').run([
                'rsync', '-r', *prefix_path_mnt(conf_dirs)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True


class ConfPurgeCommand(SubCommand):
    """kiwi conf-purge"""

    def __init__(self):
        super().__init__(
            'conf-purge',
            action="Removing all configs for",
            description="Remove all config files in target directory"
        )

    def _run_instance(self, runner, args):
        conf_target = f"{LoadedConfig.get()['runtime:storage']}/{CONF_DIRECTORY_NAME}"
        logging.info(f"Purging directories: {conf_target}")

        Rootkit().run([
            'rm', '-rf', prefix_path_mnt(conf_target)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True


class ConfCleanCommand(SubCommand):
    """kiwi conf-clean"""

    def __init__(self):
        super().__init__(
            'conf-clean',
            action="Cleaning all configs for",
            description="Cleanly sync all configs to target folder, relaunch affected projects"
        )

    def _run_instance(self, runner, args):
        result = True

        affected_projects = [
            project.conf_dir_name()
            for project in Projects.from_dir()
            if project.has_configs()
        ]

        for project_name in affected_projects:
            args.projects = project_name
            result &= runner.run('down')

        # cleanly sync configs
        result &= runner.run('conf-purge')
        result &= runner.run('conf-copy')

        # bring projects back up
        for project_name in affected_projects:
            args.projects = project_name
            result &= runner.run('up')

        return result
