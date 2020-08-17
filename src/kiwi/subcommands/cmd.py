# local
from ._subcommand import ProjectCommand
from .utils.dockercommand import DockerCommand


class CmdCommand(ProjectCommand):
    """kiwi cmd"""

    def __init__(self):
        super().__init__(
            'cmd',
            description="Run raw docker-compose command in a project"
        )

        # command string after docker-compose
        self._sub_parser.add_argument(
            'compose_cmd', metavar='cmd', type=str,
            help="runs `docker-compose <cmd>`"
        )

    def run(self, runner, config, args):
        import shlex

        # run with split compose_cmd argument
        DockerCommand('docker-compose').run(config, args, shlex.split(args.compose_cmd))
