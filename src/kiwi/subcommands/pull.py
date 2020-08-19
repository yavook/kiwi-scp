# local
from ._subcommand import ServiceCommand


class PullCommand(ServiceCommand):
    """kiwi pull"""

    def __init__(self):
        super().__init__(
            'pull', num_projects='?', num_services='*',
            action="Pulling images for",
            description="Pull images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, args, project, services):
        project.compose_run(['pull', '--ignore-pull-failures', *services])

        return True
