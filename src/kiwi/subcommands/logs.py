from ..config import LoadedConfig
from ..core import Parser

from ._utils import SubCommand, DockerCommand


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project or service"
        )

        self.get_parser().add_argument(
            '-f', '--follow', action='store_true',
            help="output appended data as log grows"
        )

        self.get_parser().add_argument(
            'project',
            help="narf"
        )

        self.get_parser().add_argument(
            'service', nargs='?',
            help="narf"
        )

    def run(self):
        config = LoadedConfig.get()

        project_name = Parser().get_args().project
        project_marker = config['markers:project']
        project_dir = f'{project_name}{project_marker}'

        environment = {
            'DOCKERNET': config['network:name'],
            'COMPOSE_PROJECT_NAME': project_name
        }

        args = ['logs', '-t']
        if Parser().get_args().follow:
            args = [*args, '-f', '--tail=10']

            DockerCommand('docker-compose').run(
                args,
                cwd=project_dir, env=environment
            )
        else:
            DockerCommand('docker-compose').run_less(
                args,
                cwd=project_dir, env=environment
            )
