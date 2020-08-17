# system
import logging
import subprocess

# local
from ._subcommand import SubCommand
from .utils.dockercommand import DockerCommand
from .utils.user_input import are_you_sure


def _find_net(config, args):
    ps = DockerCommand('docker').run(
        config, args, ['network', 'ls', '--filter', f"name={config['network:name']}", '--format', '{{.Name}}'],
        stdout=subprocess.PIPE
    )

    net_found = str(ps.stdout, 'utf-8').strip()

    return net_found == config['network:name']


class NetUpCommand(SubCommand):
    """kiwi net-up"""

    def __init__(self):
        super().__init__(
            'net-up',
            description="Create the local network hub for this instance"
        )

    def run(self, runner, config, args):
        if _find_net(config, args):
            logging.info(f"Network '{config['network:name']}' already exists")
            return True

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
            return False

        return True


class NetDownCommand(SubCommand):
    """kiwi net-down"""

    def __init__(self):
        super().__init__(
            'net-down',
            description="Remove the local network hub for this instance"
        )

    def run(self, runner, config, args):
        if not _find_net(config, args):
            logging.info(f"Network '{config['network:name']}' already removed")
            return True

        try:
            if are_you_sure("This will bring down this instance's hub network!"):
                if runner.run('down'):
                    DockerCommand('docker').run(
                        config, args,
                        ['network', 'rm', config['network:name']],
                        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )
                    logging.info(f"Network '{config['network:name']}' removed")
            else:
                return False

        except subprocess.CalledProcessError:
            logging.error(f"Error removing network '{config['network:name']}'")
            return False

        return True