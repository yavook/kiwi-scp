import logging

from ..config import LoadedConfig
from ..core import Parser

from ._utils import SubCommand, DockerCommand


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project or service(s) of a project"
        )

        self._parser.add_argument(
            '-f', '--follow', action='store_true',
            help="output appended data as log grows"
        )

        self._parser.add_argument(
            'project', type=str,
            help="select a project in this instance"
        )

        self._parser.add_argument(
            'services', metavar='service', nargs='*', type=str,
            help="select service(s) in a project"
        )

    def run(self):
        config = LoadedConfig.get()
        cli_args = Parser().get_args()

        project_name = cli_args.project
        project_marker = config['markers:project']
        project_dir = f'{project_name}{project_marker}'

        environment = {
            'KIWI_HUB_NAME': config['network:name'],
            'COMPOSE_PROJECT_NAME': project_name
        }

        args = ['logs', '-t']
        if cli_args.follow:
            args = [*args, '-f', '--tail=10']

        if cli_args.services:
            args = [*args, *cli_args.services]

        try:
            if cli_args.follow:
                DockerCommand('docker-compose').run(
                    args,
                    cwd=project_dir, env=environment
                )
            else:
                DockerCommand('docker-compose').run_less(
                    args,
                    cwd=project_dir, env=environment
                )
        except KeyboardInterrupt:
            logging.debug("Subprocess aborted.")
            print()
