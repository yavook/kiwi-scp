# local
from .utils.project import Project
from ._subcommand import ProjectCommand


class DisableCommand(ProjectCommand):
    """kiwi disable"""

    def __init__(self):
        super().__init__(
            'disable', num_projects='+',
            description="Disable whole project(s) in this instance"
        )

    def run(self, runner, config, args):
        result = True

        for project in Project.from_args(args):
            result = project.disable()

        return result
