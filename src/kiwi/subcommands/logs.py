from ._utils import SubCommand, DockerProgram


class LogsCommand(SubCommand):
    def __init__(self):
        super().__init__(
            'logs',
            description="Show logs of a project"
        )

    def run(self):
        DockerProgram('docker-compose').run(
            ['logs', '-tf', '--tail=10'],
            cwd='hello-world.project',
            env={'COMPOSE_PROJECT_NAME': 'hello-world'}
        )
