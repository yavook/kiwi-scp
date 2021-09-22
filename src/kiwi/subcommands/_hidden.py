# system
import logging
import subprocess

# local
from .._constants import CONF_DIRECTORY_NAME
from ..config import LoadedConfig
from ..executable import Executable
from ..projects import Projects
from ..rootkit import Rootkit, prefix_path_mnt
from ..subcommand import SubCommand


class ConfCopyCommand(SubCommand):
    """kiwi conf-copy"""

    def __init__(self):
        super().__init__(
            'conf-copy',
            action="Syncing all configs for", add_parser=False,
            description="Synchronize all config files to target directory"
        )

    def _run_instance(self, runner, args):
        conf_dirs = [
            project.conf_dir_name()
            for project in Projects.from_dir().filter_enabled()
            if project.has_configs()
        ]

        if conf_dirs:
            # add target directory
            conf_dirs.append(LoadedConfig.get()['runtime:storage'])
            logging.info(f"Sync directories: {conf_dirs}")

            Rootkit('rsync').run([
                'rsync', '-rpt', '--delete', *prefix_path_mnt(conf_dirs)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return True


def _find_net(net_name):
    ps = Executable('docker').run([
        'network', 'ls', '--filter', f"name={net_name}", '--format', '{{.Name}}'
    ], stdout=subprocess.PIPE)

    net_found = str(ps.stdout, 'utf-8').strip()

    return net_found == net_name


class NetUpCommand(SubCommand):
    """kiwi net-up"""

    def __init__(self):
        super().__init__(
            'net-up',
            action="Creating the local network hub for", add_parser=False,
            description="Create the local network hub for this instance"
        )

    def _run_instance(self, runner, args):
        config = LoadedConfig.get()
        net_name = config['network:name']
        net_cidr = config['network:cidr']

        if _find_net(net_name):
            logging.info(f"Network '{net_name}' already exists")
            return True

        try:
            Executable('docker').run([
                'network', 'create',
                '--driver', 'bridge',
                '--internal',
                '--subnet', net_cidr,
                net_name
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logging.info(f"Network '{net_name}' created")

        except subprocess.CalledProcessError:
            logging.error(f"Error creating network '{net_name}'")
            return False

        return True
