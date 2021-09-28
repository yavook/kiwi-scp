# system
import logging
import subprocess

# local
from ._hidden import _find_net
from ..config import LoadedConfig
from ..executable import Executable
from ..misc import are_you_sure
from ..subcommand import SubCommand


class PurgeCommand(SubCommand):
    """kiwi purge"""

    def __init__(self):
        super().__init__(
            'purge',
            action="Tearing down",
            description="Remove all running docker artifacts of this instance"
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
