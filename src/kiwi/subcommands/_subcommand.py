# local
from .utils.project import get_project_name, list_projects

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

        if not str(num_projects) == '1':
            projects = "projects"

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

        if not str(num_services) == '1':
            services = "services"

        self._sub_parser.add_argument(
            'services', metavar='service', nargs=num_services, type=str,
            help=f"select {services} in a project"
        )


class FlexCommand(ServiceCommand):
    def __init__(self, name, **kwargs):
        super().__init__(
            name, num_projects='?', num_services='*',
            **kwargs
        )

    def _run_instance(self, runner, config, args):
        result = True

        for project_name in list_projects(config):
            args.projects = project_name
            result &= runner.run(str(self))

        return result

    def _run_project(self, runner, config, args):
        pass

    def _run_services(self, runner, config, args):
        pass

    def run(self, runner, config, args):
        if 'projects' not in args or args.projects is None:
            # command for entire instance
            return self._run_instance(runner, config, args)

        elif 'services' not in args or not args.services:
            # command for whole project
            return self._run_project(runner, config, args)

        else:
            # command for service(s) inside project
            return self._run_services(runner, config, args)
