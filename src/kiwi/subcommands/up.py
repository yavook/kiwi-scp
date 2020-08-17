# system
import logging

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand
from .utils.project import get_project_name, list_projects


class UpCommand(ServiceCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', num_projects='?', num_services='*',
            description="Bring up the whole instance, a project or service(s) inside a project"
        )

    def run(self, runner, config, args):
        if 'projects' not in args or args.projects is None:
            # "up" for all projects
            for project_name in list_projects(config):
                args.projects = project_name
                runner.run('up')

            return

        if 'services' in args and args.services:
            logging.info(f"Bringing up services {args.services} in project '{get_project_name(args)}'")
        else:
            logging.info(f"Bringing up project '{get_project_name(args)}'")

        if runner.run('net-up'):
            DockerCommand('docker-compose').run(
                config, args, ['up', '-d', *args.services]
            )
            return True

        return False
