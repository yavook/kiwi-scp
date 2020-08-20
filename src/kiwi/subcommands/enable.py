# local
from ..subcommand import ProjectCommand


class EnableCommand(ProjectCommand):
    """kiwi enable"""

    def __init__(self):
        super().__init__(
            'enable', num_projects='+',
            action="Enabling",
            description="Enable project(s) in this instance"
        )

    def _run_project(self, runner, args, project):
        return project.enable()
