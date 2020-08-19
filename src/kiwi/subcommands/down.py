# local
from ..subcommand import ServiceCommand
from ..misc import are_you_sure


class DownCommand(ServiceCommand):
    """kiwi down"""

    def __init__(self):
        super().__init__(
            'down', num_projects='?', num_services='*',
            action="Bringing down",
            description="Bring down the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        if are_you_sure([
            "This will bring down the entire instance.",
            "",
            "This may not be what you intended, because:",
            " - Bringing down the instance stops ALL services in here",
        ]):
            return super()._run_instance(runner, args)

        return False

    def _run_projects(self, runner, args, projects):
        for project in projects:
            project.compose_run(['down'])

        return True

    def _run_services(self, runner, args, project, services):
        project.compose_run(['stop', *services])
        project.compose_run(['rm', '-f', *services])

        return True
