# local
from .utils.project import Project
from ._subcommand import ProjectCommand


class EnableCommand(ProjectCommand):
    """kiwi enable"""

    def __init__(self):
        super().__init__(
            'enable', num_projects='+',
            description="Enable whole project(s) in this instance"
        )

    def run(self, runner, config, args):
        result = True

        for project in Project.from_args(args):
            result = project.enable()

        return result
