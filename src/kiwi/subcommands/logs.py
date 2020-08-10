from ..core import Parser

from ._utils import SubCommand, Docker


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project"
        )

    def run(self):
        print(Docker.run_command('docker-compose', ['logs', '-tf', '--tail=10'], cwd='hello-world.project', env={'COMPOSE_PROJECT_NAME': 'hello-world'}))
