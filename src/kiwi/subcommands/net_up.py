# system
import logging
import subprocess

# local
from ._subcommand import SubCommand
from .utils.dockercommand import DockerCommand


class NetUpCommand(SubCommand):
    """kiwi net-up"""

    def __init__(self):
        super().__init__(
            'net-up',
            description="Create the local network hub for this instance"
        )

    def run(self, runner, config, args):
        ps = DockerCommand('docker').run(
            config, args, ['network', 'ls', '--filter', f"name={config['network:name']}", '--format', '{{.Name}}'],
            stdout=subprocess.PIPE
        )

        net_found = str(ps.stdout, 'utf-8').strip()

        if net_found == config['network:name']:
            logging.info(f"Network '{config['network:name']}' already exists")
            return

        try:
            DockerCommand('docker').run(
                config, args,
                [
                    'network', 'create',
                    '--driver', 'bridge',
                    '--internal',
                    '--subnet', config['network:cidr'],
                    config['network:name']
                ],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
            logging.info(f"Network '{config['network:name']}' created")

        except subprocess.CalledProcessError:
            logging.error(f"Error creating network '{config['network:name']}'")
