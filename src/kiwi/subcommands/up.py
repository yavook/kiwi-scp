# local
from ._subcommand import ServiceCommand


class UpCommand(ServiceCommand):
    """kiwi up"""

    def __init__(self):
        super().__init__(
            'up', num_projects='?', num_services='*',
            action="Bringing up",
            description="Bring up the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        if runner.run('conf-copy'):
            return super()._run_instance(runner, args)

        return False

    def _run_services(self, runner, args, project, services):
        if runner.run('net-up'):
            project.compose_run(['up', '-d', *services])
            return True

        return False
