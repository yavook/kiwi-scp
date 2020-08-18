# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand
from .utils.misc import are_you_sure


class DownCommand(FlexCommand):
    """kiwi down"""

    def __init__(self):
        super().__init__(
            'down', "Bringing down",
            description="Bring down the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, config, args):
        if are_you_sure([
            "This will bring down the entire instance.",
            "",
            "This may not be what you intended, because:",
            " - Bringing down the instance stops ALL services in here",
        ]):
            return super()._run_instance(runner, config, args)

        return False

    def _run_project(self, runner, config, args):
        DockerCommand('docker-compose').run(
            config, args, ['down']
        )
        return True

    def _run_services(self, runner, config, args, services):
        DockerCommand('docker-compose').run(
            config, args, ['stop', *services]
        )
        DockerCommand('docker-compose').run(
            config, args, ['rm', '-f', *services]
        )
        return True
