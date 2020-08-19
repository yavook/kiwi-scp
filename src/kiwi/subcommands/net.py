# system
import logging
import subprocess

# local
from ._subcommand import SubCommand

# parent
from ..config import LoadedConfig
from ..executable import Executable
from ..misc import are_you_sure


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
            action="Creating the local network hub for",
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


class NetDownCommand(SubCommand):
    """kiwi net-down"""

    def __init__(self):
        super().__init__(
            'net-down',
            action="Removing the local network hub for",
            description="Remove the local network hub for this instance"
        )

    def _run_instance(self, runner, args):
        net_name = LoadedConfig.get()['network:name']

        if not _find_net(net_name):
            logging.info(f"Network '{net_name}' does not exist")
            return True

        try:
            if are_you_sure("This will bring down this instance's hub network!"):
                if runner.run('down'):
                    Executable('docker').run([
                        'network', 'rm', net_name
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    logging.info(f"Network '{net_name}' removed")
            else:
                return False

        except subprocess.CalledProcessError:
            logging.error(f"Error removing network '{net_name}'")
            return False

        return True
