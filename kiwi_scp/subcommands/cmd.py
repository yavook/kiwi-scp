# system
import logging

# local
from ..subcommand import ProjectCommand


class CmdCommand(ProjectCommand):
    """kiwi cmd"""

    def __init__(self):
        super().__init__(
            'cmd', num_projects=1,
            action="Running docker-compose in",
            description="Run raw docker-compose command in a project"
        )

        # command for docker-compose
        self._sub_parser.add_argument(
            'compose_cmd', metavar='cmd', type=str,
            help="command for 'docker-compose'"
        )

        # arguments for docker-compose command
        self._sub_parser.add_argument(
            'compose_args', metavar='arg', nargs='*', type=str,
            help="arguments for 'docker-compose' commands"
        )

    def _run_project(self, runner, args, project):
        if args.unknowns:
            args.compose_args = [*args.compose_args, *args.unknowns]
            args.unknowns = []

            logging.debug(f"Updated args: {args}")

        # run with split compose_cmd argument
        project.compose_run([args.compose_cmd, *args.compose_args])

        return True
