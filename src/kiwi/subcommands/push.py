# local
from ._subcommand import ServiceCommand


class PushCommand(ServiceCommand):
    """kiwi push"""

    def __init__(self):
        super().__init__(
            'push', num_projects='?', num_services='*',
            action="Pushing images for",
            description="Push images for the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, args, project, services):
        project.compose_run(['push', *services])

        return True
