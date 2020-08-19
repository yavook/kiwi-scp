# local
from ..subcommand import ServiceCommand


class BuildCommand(ServiceCommand):
    """kiwi build"""

    def __init__(self):
        super().__init__(
            'build', num_projects='?', num_services='*',
            action="Building images for",
            description="Build images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, args, project, services):
        project.compose_run(['build', '--pull', *services])

        return True
