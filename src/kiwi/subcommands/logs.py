from ..core import Parser

from ._utils import SubCommand, DockerProgram


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project or service"
        )

        self.get_parser().add_argument(
            '-f', '--follow',
            action='store_true',
            help="output appended data as log grows"
        )

    def run(self):
        args = ['logs', '-t']
        if Parser().get_args().follow:
            args = [*args, '-f', '--tail=10']

        DockerProgram('docker-compose').run(
            args,
            cwd='hello-world.project',
            env={'COMPOSE_PROJECT_NAME': 'hello-world'}
        )
