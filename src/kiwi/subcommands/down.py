# system
import logging
import subprocess

# local
from ._hidden import _find_net
from ..subcommand import ServiceCommand
from ..config import LoadedConfig
from ..executable import Executable
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
        net_name = LoadedConfig.get()['network:name']

        if are_you_sure([
            "This will bring down the entire instance.",
            "",
            "This may not be what you intended, because:",
            " - Bringing down the instance stops ALL services in here",
        ]):
            if super()._run_instance(runner, args):
                # remove the hub network afterwards
                if _find_net(net_name):
                    Executable('docker').run([
                        'network', 'rm', net_name
                    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

                    logging.info(f"Network '{net_name}' removed")

                else:
                    logging.info(f"Network '{net_name}' does not exist")

                return True

        return False

    def _run_project(self, runner, args, project):
        project.compose_run(['down'])
        return True

    def _run_services(self, runner, args, project, services):
        project.compose_run(['stop', *services])
        project.compose_run(['rm', '-f', *services])

        return True
