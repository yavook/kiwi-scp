# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand


class UpCommand(FlexCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', "Bringing up",
            description="Bring up the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, config, args):
        if runner.run('conf-copy'):
            return super()._run_instance(runner, config, args)

        return False

    def _run_services(self, runner, config, args, services):
        if runner.run('net-up'):
            DockerCommand('docker-compose').run(
                config, args, ['up', '-d', *services]
            )
            return True

        return False
