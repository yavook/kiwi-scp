# system
import logging
import os
import yaml

# local
from ..subcommand import ServiceCommand
from ..project import Project
from ..projects import Projects


def _print_list(strings):
    if isinstance(strings, str):
        print(f" - {strings}")

    elif isinstance(strings, Project):
        _print_list(strings.get_name())

    elif isinstance(strings, list):
        for string in strings:
            _print_list(string)

    else:
        _print_list(list(strings))


class InspectCommand(ServiceCommand):
    """kiwi inspect"""

    def __init__(self):
        super().__init__(
            'inspect', num_projects='?', num_services='*',
            action="Inspecting",
            description="Inspect projects in this instance, services inside a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        print(f"kiwi-config instance at '{os.getcwd()}'")
        print("#########")
        projects = Projects.from_dir()

        enabled_projects = projects.filter_enabled()
        if enabled_projects:
            print(f"Enabled projects:")
            _print_list(enabled_projects)

        disabled_projects = projects.filter_disabled()
        if disabled_projects:
            print(f"Disabled projects:")
            _print_list(disabled_projects)

        return True

    def _run_projects(self, runner, args, projects):
        project = projects[0]
        if not project.exists():
            logging.warning(f"Project '{project.get_name()}' not found")
            return False

        print(f"Services in project '{project.get_name()}':")
        print("#########")

        with open(project.compose_file_name(), 'r') as stream:
            try:
                docker_compose_yml = yaml.safe_load(stream)
                _print_list(docker_compose_yml['services'].keys())

            except yaml.YAMLError as exc:
                logging.error(exc)

        return True

    def _run_services(self, runner, args, project, services):
        if not project.exists():
            logging.error(f"Project '{project.get_name()}' not found")
            return False

        print(f"Configuration of services {services} in project '{project.get_name()}':")
        print("#########")

        with open(project.compose_file_name(), 'r') as stream:
            try:
                docker_compose_yml = yaml.safe_load(stream)

                for service_name in services:
                    try:
                        print(yaml.dump(
                            {service_name: docker_compose_yml['services'][service_name]},
                            default_flow_style=False, sort_keys=False
                        ).strip())
                    except KeyError:
                        logging.error(f"Service '{service_name}' not found")

                return True

            except yaml.YAMLError as exc:
                logging.error(exc)

        return False
