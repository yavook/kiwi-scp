# system
import logging

# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand
from .utils.project import get_project_name, list_projects


class UpCommand(FlexCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', description="Bring up the whole instance, a project or service(s) inside a project"
        )

    def _run_project(self, runner, config, args):
        logging.info(f"Bringing up project '{get_project_name(args)}'")

        DockerCommand('docker-compose').run(
            config, args, ['up', '-d']
        )
        return True

    def _run_services(self, runner, config, args):
        logging.info(f"Bringing up services {args.services} in project '{get_project_name(args)}'")

        DockerCommand('docker-compose').run(
            config, args, ['up', '-d', *args.services]
        )
        return True
