# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand


class PullCommand(FlexCommand):
    """kiwi pull"""

    def __init__(self):
        super().__init__(
            'pull', "Pulling images",
            description="Pull images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, config, args, services):
        DockerCommand('docker-compose').run(
            config, args, ['pull', '--ignore-pull-failures', *services]
        )
        return True
