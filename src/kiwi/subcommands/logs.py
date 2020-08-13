# system
import logging

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


class LogsCommand(ServiceCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project or service(s) of a project"
        )

        # -f switch: Follow logs
        self._sub_parser.add_argument(
            '-f', '--follow', action='store_true',
            help="output appended data as log grows"
        )

    def run(self, config, args):
        compose_args = ['logs', '-t']
        if args.follow:
            compose_args = [*compose_args, '-f', '--tail=10']

        if args.services:
            compose_args = [*compose_args, *args.services]

        try:
            if args.follow:
                DockerCommand('docker-compose').run(config, args, compose_args)
            else:
                DockerCommand('docker-compose').run_less(config, args, compose_args)

        except KeyboardInterrupt:
            logging.debug("Subprocess aborted.")
            print()
