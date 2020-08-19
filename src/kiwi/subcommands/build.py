# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand


class BuildCommand(ServiceCommand):
    """kiwi build"""

    def __init__(self):
        super().__init__(
            'build', num_projects='?', num_services='*',
            action="Building images for",
            description="Build images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, args, project, services):
        DockerCommand('docker-compose').run(project, [
            'build', '--pull', *services
        ])
        return True
