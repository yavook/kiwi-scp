# local
from .utils.project import Projects
from ._subcommand import ProjectCommand


class EnableCommand(ProjectCommand):
    """kiwi enable"""

    def __init__(self):
        super().__init__(
            'enable', num_projects='+',
            description="Enable whole project(s) in this instance"
        )

    def run(self, runner, config, args):
        return all([
            project.enable()
            for project in Projects.from_args(args)
        ])
