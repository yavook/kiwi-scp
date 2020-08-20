from ..projects import Projects
from ..subcommand import SubCommand


class CleanCommand(SubCommand):
    """kiwi clean"""

    def __init__(self):
        super().__init__(
            'clean',
            action="Cleaning all configs for",
            description="Cleanly sync all configs to target folder, then relaunch affected projects"
        )

    def _run_instance(self, runner, args):
        result = True

        affected_projects = [
            project.get_name()
            for project in Projects.from_dir()
            if project.has_configs()
        ]

        for project_name in affected_projects:
            args.projects = project_name
            result &= runner.run('down')

        # cleanly sync configs
        result &= runner.run('conf-purge')
        result &= runner.run('conf-copy')

        # bring projects back up
        for project_name in affected_projects:
            args.projects = project_name
            result &= runner.run('up')

        return result
