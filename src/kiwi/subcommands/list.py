# system
import logging
import os
import subprocess

# local
from ._subcommand import FlexCommand
from .utils.dockercommand import DockerCommand
from .utils.misc import list_projects, get_first_project_name, get_project_dir


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
        print(f"Projects in instance {os.getcwd()}:")
        print("")

        _print_list(list_projects(config))

        return True

    def _run_project(self, runner, config, args):
        project_name = get_first_project_name(args)
        print(f"Services in project '{project_name}':")
        print("")

        ps = DockerCommand('docker-compose').run(
            config, args, ['config', '--services'],
            stdout=subprocess.PIPE
        )
        _print_list(ps.stdout)

        return True

    def _run_services(self, runner, config, args, services):
        import yaml

        project_name = get_first_project_name(args)
        project_dir = get_project_dir(config, project_name)
        print(f"Configuration of services {services} in project '{project_name}':")
        print("")

        with open(os.path.join(project_dir, 'docker-compose.yml'), 'r') as stream:
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
