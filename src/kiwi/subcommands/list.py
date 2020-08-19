# system
import logging
import os
import subprocess
import yaml

# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand
from .utils.project import Projects


def _print_list(strings):
    if isinstance(strings, list):
        for string in strings:
            print(f" - {string}")

    elif isinstance(strings, str):
        _print_list(strings.strip().split('\n'))

    elif isinstance(strings, bytes):
        _print_list(str(strings, 'utf-8'))


class ListCommand(FlexCommand):
    """kiwi list"""

    def __init__(self):
        super().__init__(
            'list', "Listing",
            description="List projects in this instance, services inside a project or service(s) inside a project"
        )

    def _run_instance(self, runner, config, args):
        print(f"kiwi-config instance at '{os.getcwd()}'")
        print("#########")
        projects = Projects.all()

        enableds = [
            project.get_name()
            for project in projects
            if project.is_enabled()
        ]

        if enableds:
            print(f"Enabled projects:")
            _print_list(enableds)

        disableds = [
            project.get_name()
            for project in projects
            if project.is_disabled()
        ]

        if disableds:
            print(f"Disabled projects:")
            _print_list(disableds)

        return True

    def _run_project(self, runner, config, args):
        project = Projects.from_args(args)[0]

        if not project.exists():
            logging.error(f"Project '{project.get_name()}' not found")
            return False

        print(f"Services in project '{project.get_name()}':")
        print("#########")

        ps = DockerCommand('docker-compose').run(
            config, args, ['config', '--services'],
            stdout=subprocess.PIPE
        )

        _print_list(ps.stdout)
        return True

    def _run_services(self, runner, config, args, services):
        project = Projects.from_args(args)[0]

        if not project.exists():
            logging.error(f"Project '{project.get_name()}' not found")
            return False

        print(f"Configuration of services {services} in project '{project.get_name()}':")
        print("#########")

        with open(project.compose_file_name(), 'r') as stream:
            try:
                docker_compose_yml = yaml.safe_load(stream)

                for service_name in services:
                    print(yaml.dump(
                        {service_name: docker_compose_yml['services'][service_name]},
                        default_flow_style=False, sort_keys=False
                    ).strip())

                return True

            except yaml.YAMLError as exc:
                logging.error(exc)

        return False
