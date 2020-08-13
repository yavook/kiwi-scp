# system
import logging
import subprocess

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


def _service_has_shell(config, args, exec_service, try_shell):
    try:
        # test if desired shell exists
        DockerCommand('docker-compose').run(
            config, args, [*exec_service, '/bin/sh', '-c', f"which {try_shell}"],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return True

    except subprocess.CalledProcessError:
        # fallback
        logging.info(f"Shell '{try_shell}' not found in container")
        return False


class ShellCommand(ServiceCommand):
    def __init__(self):
        super().__init__(
            'sh', 1,
            description="Spawn shell inside project's service"
        )

        # -s switch: Select shell
        self._sub_parser.add_argument(
            '-s', '--shell', type=str, default="/bin/bash",
            help="shell to spawn"
        )

    def run(self, config, args):
        try:
            exec_service = ['exec', args.services[0]]
            exec_shell = args.shell

            if not _service_has_shell(config, args, exec_service, exec_shell):
                # fallback
                exec_shell = '/bin/bash'

                if not _service_has_shell(config, args, exec_service, exec_shell):
                    exec_shell = '/bin/sh'

            # spawn shell
            DockerCommand('docker-compose').run(
                config, args, [*exec_service, exec_shell]
            )

        except KeyboardInterrupt:
            logging.debug("Subprocess aborted.")
            print()
