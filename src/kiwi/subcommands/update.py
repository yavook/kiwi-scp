# local
from ._subcommand import ServiceCommand
from .utils.misc import are_you_sure


class UpdateCommand(ServiceCommand):
    """kiwi update"""

    def __init__(self):
        super().__init__(
            'update',  num_projects='?', num_services='*',
            action="Updating",
            description="Update the whole instance, a project or service(s) inside a project"
        )

    def _run_instance(self, runner, args):
        if are_you_sure([
            "This will update the entire instance at once.",
            "",
            "This is probably not what you intended, because:",
            " - Updates may take a long time",
            " - Updates may break beloved functionality",
        ]):
            return super()._run_instance(runner, args)

        return False

    def _run_services(self, runner, args, project, services):
        result = True

        result &= runner.run('build')
        result &= runner.run('pull')
        result &= runner.run('conf-copy')
        result &= runner.run('down')
        result &= runner.run('up')

        return result
