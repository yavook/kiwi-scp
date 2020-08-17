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
