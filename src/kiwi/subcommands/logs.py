import logging

from ._subcommand import SubCommand
from .utils.dockercommand import DockerCommand


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project or service(s) of a project"
        )

        self._sub_parser.add_argument(
            '-f', '--follow', action='store_true',
            help="output appended data as log grows"
        )

        self._sub_parser.add_argument(
            'project', type=str,
            help="select a project in this instance"
        )

        self._sub_parser.add_argument(
            'services', metavar='service', nargs='*', type=str,
            help="select service(s) in a project"
        )

    def run(self, config, args):
        project_name = args.project
        project_marker = config['markers:project']
        project_dir = f'{project_name}{project_marker}'

        environment = {
            'KIWI_HUB_NAME': config['network:name'],
            'COMPOSE_PROJECT_NAME': project_name
        }

        process_args = ['logs', '-t']
        if args.follow:
            process_args = [*process_args, '-f', '--tail=10']

        if args.services:
            process_args = [*process_args, *args.services]

        try:
            if args.follow:
                DockerCommand('docker-compose').run(
                    process_args,
                    cwd=project_dir, env=environment
                )
            else:
                DockerCommand('docker-compose').run_less(
                    process_args,
                    cwd=project_dir, env=environment
                )
        except KeyboardInterrupt:
            logging.debug("Subprocess aborted.")
            print()
