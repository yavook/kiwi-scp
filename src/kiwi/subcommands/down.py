# system
import logging

# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand
from .utils.project import get_project_name, list_projects
from .utils.user_input import are_you_sure


class DownCommand(FlexCommand):
    """kiwi down"""

    def __init__(self):
        super().__init__(
            'down', description="Bring down the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, config, args):
        if are_you_sure("This will bring down the entire instance."):
            super()._run_instance(runner, config, args)

        return False

    def _run_project(self, runner, config, args):
        logging.info(f"Bringing down project '{get_project_name(args)}'")

        DockerCommand('docker-compose').run(
            config, args, ['down']
        )
        return True

    def _run_services(self, runner, config, args):
        logging.info(f"Bringing down services {args.services} in project '{get_project_name(args)}'")

        DockerCommand('docker-compose').run(
            config, args, ['stop', *args.services]
        )
        DockerCommand('docker-compose').run(
            config, args, ['rm', '-f', *args.services]
        )
        return True
