# local
from ..subcommand import ProjectCommand


class DisableCommand(ProjectCommand):
    """kiwi disable"""

    def __init__(self):
        super().__init__(
            'disable', num_projects='+',
            action="Disabling",
            description="Disable project(s) in this instance"
        )

    def _run_project(self, runner, args, project):
        return project.disable()
