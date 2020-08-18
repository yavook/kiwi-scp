# local
from ._subcommand import FlexCommand


class UpdateCommand(FlexCommand):
    """kiwi update"""

    def __init__(self):
        super().__init__(
            'update', "Updating",
            description="Update the whole instance, a project or service(s) inside a project"
        )

    def _run_services(self, runner, config, args, services):
        result = runner.run('build')
        result &= runner.run('pull')
        result &= runner.run('conf-copy')
        result &= runner.run('down')
        result &= runner.run('up')

        return result
