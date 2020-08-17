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

    def __init__(self, name, **kwargs):
        super().__init__(
            name,
            **kwargs
        )

        self._sub_parser.add_argument(
            'project', type=str,
            help="select a project in this instance"
        )


class ServiceCommand(ProjectCommand):
    """this command concerns service(s) in a project"""

    def __init__(self, name, nargs=1, **kwargs):
        super().__init__(
            name,
            **kwargs
        )

        services = "service"

        if not nargs == 1:
            services = "services"

        self._sub_parser.add_argument(
            'services', metavar='service', nargs=nargs, type=str,
            help=f"select {services} in a project"
        )
