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
        logging.info(f"Shell '{shell}' not found in container")
        return False


class ShCommand(ServiceCommand):
    def __init__(self):
        super().__init__(
            'sh',
            description="Spawn shell inside a project's service"
        )

        # -s switch: Select shell
        self._sub_parser.add_argument(
            '-s', '--shell', type=str, default="/bin/bash",
            help="shell to spawn"
        )

    def run(self, config, args):
        compose_cmd = ['exec', args.services[0]]
        shell = args.shell

        if not _service_has_shell(config, args, compose_cmd, shell):
            # fallback
            shell = '/bin/bash'

            if not _service_has_shell(config, args, compose_cmd, shell):
                # safe fallback
                shell = '/bin/sh'

        # spawn shell
        DockerCommand('docker-compose').run(
            config, args, [*compose_cmd, shell]
        )
