# local
from ..subcommand import ProjectCommand


class EnableCommand(ProjectCommand):
    """kiwi enable"""

    def __init__(self):
        super().__init__(
            'enable', num_projects='+',
            action="Enabling",
            description="Enable whole project(s) in this instance"
        )

    def _run_projects(self, runner, args, projects):
        return all([
            project.enable()
            for project in projects
        ])
