# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


class PullCommand(ServiceCommand):
    """kiwi pull"""

    def __init__(self):
        super().__init__(
            'pull', num_projects='?', num_services='*',
            action="Pulling images for",
            description="Pull images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, args, project, services):
        DockerCommand('docker-compose').run(project, [
            'pull', '--ignore-pull-failures', *services
        ])
        return True
