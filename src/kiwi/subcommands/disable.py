# local
from .utils.project import Projects
from ._subcommand import ProjectCommand


class DisableCommand(ProjectCommand):
    """kiwi disable"""

    def __init__(self):
        super().__init__(
            'disable', num_projects='+',
            description="Disable whole project(s) in this instance"
        )

    def run(self, runner, config, args):
        return all([
            project.disable()
            for project in Projects.from_args(args)
        ])
