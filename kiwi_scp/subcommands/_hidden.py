# system
import logging
import subprocess

# local
from ..config import LoadedConfig
from ..executable import Executable
from ..subcommand import SubCommand


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
