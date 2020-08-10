from ..core import Parser

from ._utils import SubCommand, Docker


class LogsCommand(SubCommand):
    command = 'logs'

    @classmethod
    def setup(cls):
        parser = Parser.get_subparsers().add_parser(
            cls.command,
            description="Show logs of a project"
        )

    @classmethod
    def run(cls):
        print(Docker.run_command('docker-compose', ['logs', '-tf', '--tail=10'], cwd='hello-world.project', env={'COMPOSE_PROJECT_NAME': 'hello-world'}))
