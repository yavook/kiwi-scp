# local
from ..misc import are_you_sure
from ..subcommand import ServiceCommand


class RestartCommand(ServiceCommand):
    """kiwi restart"""

    def __init__(self):
        super().__init__(
            'restart', num_projects='?', num_services='*',
            action="Restarting",
            description="Restart the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        if are_you_sure([
            "This will restart the entire instance."
        ]):
            return super()._run_instance(runner, args)

        return False

    def _run_services(self, runner, args, project, services):
        project.compose_run(['restart', *services])
        return True
