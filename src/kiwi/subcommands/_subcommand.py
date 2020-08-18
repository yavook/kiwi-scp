# system
import logging

# local
from .utils.misc import get_first_project_name, get_services, list_projects

# parent
from ..parser import Parser


class SubCommand:
    """represents kiwi [anything] command"""

    # actual command string
    __name = None
    # command parser
    _sub_parser = None

    def __init__(self, name, **kwargs):
        self.__name = name
        self._sub_parser = Parser().get_subparsers().add_parser(
            name,
            **kwargs
        )

    def __str__(self):
        return self.__name

    def run(self, runner, config, args):
        """actually run command with this dir's config and parsed CLI args"""
        pass


class ProjectCommand(SubCommand):
    """this command concerns a project in current instance"""

    def __init__(self, name, num_projects, **kwargs):
        super().__init__(
            name,
            **kwargs
        )

        projects = "a project"

        if not num_projects == 1:
            projects = "project(s)"

        self._sub_parser.add_argument(
            'projects', metavar='project', nargs=num_projects, type=str,
            help=f"select {projects} in this instance"
        )


class ServiceCommand(ProjectCommand):
    """this command concerns service(s) in a project"""

    def __init__(self, name, num_projects, num_services, **kwargs):
        super().__init__(
            name, num_projects=num_projects,
            **kwargs
        )

        services = "a service"

        if not num_services == 1:
            services = "service(s)"

        self._sub_parser.add_argument(
            'services', metavar='service', nargs=num_services, type=str,
            help=f"select {services} in a project"
        )


class FlexCommand(ServiceCommand):
    """this command concerns the entire instance, a whole project or just service(s) in a project"""

    __action = None

    def __init__(self, name, action='', **kwargs):
        super().__init__(
            name, num_projects='?', num_services='*',
            **kwargs
        )

        if not action:
            # default action string
            self.__action = f"Running '{str(self)}' for"
        else:
            self.__action = action

    def _run_instance(self, runner, config, args):
        result = True

        for project_name in list_projects(config):
            args.projects = project_name
            result &= runner.run(str(self))

        return result

    def _run_project(self, runner, config, args):
        return self._run_services(runner, config, args, [])

    def _run_services(self, runner, config, args, services):
        pass

    def run(self, runner, config, args):
        project_name = get_first_project_name(args)
        services = get_services(args)

        if project_name is None:
            # no project given, run for entire instance
            logging.info(f"{self.__action} this instance")
            return self._run_instance(runner, config, args)

        if not services:
            # no services given, run for whole project
            logging.info(f"{self.__action} project '{project_name}'")
            return self._run_project(runner, config, args)

        # run for service(s) inside project
        logging.info(f"{self.__action} services {services} in project '{project_name}'")
        return self._run_services(runner, config, args, services)
