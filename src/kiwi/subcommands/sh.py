# system
import logging
import subprocess

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


def _service_has_shell(config, args, compose_cmd, shell):
    try:
        # test if desired shell exists
        DockerCommand('docker-compose').run(
            config, args, [*compose_cmd, '/bin/sh', '-c', f"which {shell}"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True

    except subprocess.CalledProcessError:
        # fallback
        return False


def _find_shell(config, args, compose_cmd):
    # as a last resort, fallback to "sh"
    shells = ['/bin/sh', 'sh']

    # load favorite shells from config
    if config['runtime:shells']:
        shells = [*config['runtime:shells'], *shells]

    # consider shell from args
    if args.shell:
        shells = [args.shell, *shells]

    logging.debug(f"Shells priority: {shells}")

    # actually try shells
    for i, shell in enumerate(shells):
        if _service_has_shell(config, args, compose_cmd, shell):
            # shell found
            logging.debug(f"Using shell '{shell}'")
            return shell
        elif i + 1 < len(shells):
            # not found, try next
            logging.info(f"Shell '{shell}' not found in container, trying '{shells[i+1]}'")
        else:
            # not found, search exhausted
            logging.error(f"None of the shells {shells} found in container, please provide -s SHELL!")
            return None


class ShCommand(ServiceCommand):
    def __init__(self):
        super().__init__(
            'sh',
            description="Spawn shell inside a project's service"
        )

        # -s switch: Select shell
        self._sub_parser.add_argument(
            '-s', '--shell', type=str,
            help="shell to spawn"
        )

    def run(self, config, args):
        compose_cmd = ['exec', args.services[0]]
        shell = _find_shell(config, args, compose_cmd)

        if shell:
            # spawn shell
            DockerCommand('docker-compose').run(
                config, args, [*compose_cmd, shell]
            )
