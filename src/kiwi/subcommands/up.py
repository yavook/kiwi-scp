# system
import logging

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand
from .utils.project import list_projects


class UpCommand(ServiceCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', num_projects='?', num_services='*',
            description="Start the whole instance, a project or service(s) inside a project"
        )

    def run(self, runner, config, args):
        if args.projects is None:
            # "up" for all projects
            for project_name in list_projects(config):
                logging.info(f"Bringing up project '{project_name}'")
                args.projects = project_name

                runner.run('up')

            return

        runner.run('net-up')
        DockerCommand('docker-compose').run(
            config, args, ['up', '-d', *args.services]
        )
