# system
import logging

# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand


class UpCommand(FlexCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', description="Bring up the whole instance, a project or service(s) inside a project"
        )

    def _run_project(self, runner, config, args, project_name):
        logging.info(f"Bringing up project '{project_name}'")

        DockerCommand('docker-compose').run(
            config, args, ['up', '-d']
        )
        return True

    def _run_services(self, runner, config, args, project_name, services):
        logging.info(f"Bringing up services {services} in project '{project_name}'")

        DockerCommand('docker-compose').run(
            config, args, ['up', '-d', *services]
        )
        return True
