# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


class LogsCommand(ServiceCommand):
    """kiwi logs"""

    def __init__(self):
        super().__init__(
            'logs', num_projects=1, num_services='*',
            action="Showing logs of",
            description="Show logs of a project or service(s) of a project"
        )

        # -f switch: Follow logs
        self._sub_parser.add_argument(
            '-f', '--follow', action='store_true',
            help="output appended data as log grows"
        )

    def _run_services(self, runner, args, project, services):
        # include timestamps
        compose_cmd = ['logs', '-t']

        # handle following the log output
        if args.follow:
            compose_cmd = [*compose_cmd, '-f', '--tail=10']

        # append if one or more services are given
        if services:
            compose_cmd = [*compose_cmd, *args.services]

        # use 'less' viewer if output will be static
        if args.follow:
            DockerCommand('docker-compose').run(project, compose_cmd)
        else:
            DockerCommand('docker-compose').run_less(project, compose_cmd)

        return True
