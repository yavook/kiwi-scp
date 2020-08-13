# system
import logging

# local
from ._subcommand import ProjectCommand
from .utils.dockercommand import DockerCommand


class CmdCommand(ProjectCommand):
    def __init__(self):
        super().__init__(
            'cmd',
            description="Run raw docker-compose command in a project"
        )

        # arguments for docker-compose command
        self._sub_parser.add_argument(
            'compose_cmd', metavar='cmd', type=str,
            help="runs `docker-compose <cmd>"
        )

    def run(self, config, args):
        try:
            import shlex
            DockerCommand('docker-compose').run(config, args, shlex.split(args.compose_cmd))

        except KeyboardInterrupt:
            logging.debug("Subprocess aborted.")
            print()
