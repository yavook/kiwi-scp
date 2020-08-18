# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand


class BuildCommand(FlexCommand):
    """kiwi build"""

    def __init__(self):
        super().__init__(
            'build', "Building images",
            description="Build images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, config, args, services):
        DockerCommand('docker-compose').run(
            config, args, ['build', '--pull', *services]
        )
        return True
