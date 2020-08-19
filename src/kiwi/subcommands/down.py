# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand
from .utils.misc import are_you_sure


class DownCommand(ServiceCommand):
    """kiwi down"""

    def __init__(self):
        super().__init__(
            'down', num_projects='?', num_services='*',
            action="Bringing down",
            description="Bring down the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        if are_you_sure([
            "This will bring down the entire instance.",
            "",
            "This may not be what you intended, because:",
            " - Bringing down the instance stops ALL services in here",
        ]):
            return super()._run_instance(runner, args)

        return False

    def _run_projects(self, runner, args, projects):
        for project in projects:
            DockerCommand('docker-compose').run(project, [
                'down'
            ])
        return True

    def _run_services(self, runner, args, project, services):
        DockerCommand('docker-compose').run(project, [
            'stop', *services
        ])
        DockerCommand('docker-compose').run(project, [
            'rm', '-f', *services
        ])
        return True
