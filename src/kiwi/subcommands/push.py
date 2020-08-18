# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand


class PushCommand(FlexCommand):
    """kiwi push"""

    def __init__(self):
        super().__init__(
            'push', "Pushing images for",
            description="Push images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, config, args, services):
        DockerCommand('docker-compose').run(
            config, args, ['push', *services]
        )
        return True
