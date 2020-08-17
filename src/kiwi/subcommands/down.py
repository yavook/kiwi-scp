# system
import logging

# local
from ._subcommand import ServiceCommand
from .utils.dockercommand import DockerCommand
from .utils.project import get_project_name, list_projects
from .utils.user_input import are_you_sure


class DownCommand(ServiceCommand):
    """kiwi down"""

    def __init__(self):
        super().__init__(
            'down', num_projects='?', num_services='*',
            description="Bring down the whole instance, a project or service(s) inside a project"
        )

    def run(self, runner, config, args):
        if 'projects' not in args or args.projects is None:
            # "down" for all projects
            if are_you_sure("This will bring down the entire instance."):
                for project_name in list_projects(config):
                    args.projects = project_name
                    runner.run('down')
            return

        if 'services' in args and args.services:
            # "down" for service(s) inside project
            logging.info(f"Bringing down services {args.services} in project '{get_project_name(args)}'")

            DockerCommand('docker-compose').run(
                config, args, ['stop', *args.services]
            )
            DockerCommand('docker-compose').run(
                config, args, ['rm', '-f', *args.services]
            )

        else:
            # "down" for project
            logging.info(f"Bringing down project '{get_project_name(args)}'")

            DockerCommand('docker-compose').run(
                config, args, ['down']
            )
