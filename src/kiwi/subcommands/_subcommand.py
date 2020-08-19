# system
import logging
import os

# local
from .utils.project import Projects

# parent
from ..parser import Parser


class SubCommand:
    """represents kiwi [anything] command"""

    # actual command string
    __name = None
    # command parser
    _sub_parser = None

    _action = None

    def __init__(self, name, action='', add_parser=True, **kwargs):
        self.__name = name
        if add_parser:
            self._sub_parser = Parser().get_subparsers().add_parser(
                name,
                **kwargs
            )

        if not action:
            # default action string
            self._action = f"Running '{str(self)}' for"
        else:
            self._action = action

    def __str__(self):
        return self.__name

    def _run_instance(self, runner, args):
        pass

    def run(self, runner, args):
        """actually run command with parsed CLI args"""

        # run for entire instance
        logging.info(f"{self._action} kiwi-config instance at '{os.getcwd()}'")
        return self._run_instance(runner, args)


class ProjectCommand(SubCommand):
    """this command concerns a project in current instance"""

    def __init__(self, name, num_projects, action='', add_parser=True, **kwargs):
        super().__init__(
            name, action=action, add_parser=add_parser,
            **kwargs
        )

        if num_projects == 1:
            projects = "a project"
        else:
            projects = "project(s)"

        self._sub_parser.add_argument(
            'projects', metavar='project', nargs=num_projects, type=str,
            help=f"select {projects} in this instance"
        )

    def _run_instance(self, runner, args):
        # default: run for all enabled projects
        return self._run_projects(runner, args, Projects.from_dir().filter_enabled())

    def _run_projects(self, runner, args, projects):
        pass

    def run(self, runner, args):
        projects = Projects.from_args(args)

        if not projects.empty():
            # project(s) given
            logging.info(f"{self._action} projects {projects}")
            return self._run_projects(runner, args, projects)

        else:
            return super().run(runner, args)


class ServiceCommand(ProjectCommand):
    """this command concerns service(s) in a project"""

    def __init__(self, name, num_projects, num_services, action='', add_parser=True, **kwargs):
        super().__init__(
            name, num_projects=num_projects, action=action, add_parser=add_parser,
            **kwargs
        )

        if (isinstance(num_projects, str) and num_projects == '*') \
                or (isinstance(num_projects, int) and num_projects > 1):
            logging.warning(f"Invalid choice for project count: {num_projects}")

        if num_services == 1:
            services = "a service"
        else:
            services = "service(s)"

        self._sub_parser.add_argument(
            'services', metavar='service', nargs=num_services, type=str,
            help=f"select {services} in a project"
        )

    def _run_projects(self, runner, args, projects):
        result = True

        # default: run without services for all given
        for project in projects:
            result &= self._run_services(runner, args, project, [])

        return result

    def _run_services(self, runner, args, project, services):
        pass

    def run(self, runner, args):
        if 'services' in args and args.services:
            project = Projects.from_args(args)[0]

            # run for service(s) inside project
            logging.info(f"{self._action} project '{project.get_name()}', services {args.services}")
            return self._run_services(runner, args, project, args.services)

        else:
            return super().run(runner, args)
