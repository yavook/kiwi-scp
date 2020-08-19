# system
import logging
import os
import subprocess

# local
from .executable import Executable
from .project import Projects

# parent
from ..._constants import CONF_DIRECTORY_NAME
from ...parser import Parser
from ...config import LoadedConfig


def _update_kwargs(**kwargs):
    config = LoadedConfig.get()
    projects = Projects.from_args(Parser().get_args())

    # project given in args: command affects a project in this instance
    if projects:
        project = projects[0]

        # execute command in project directory
        kwargs['cwd'] = project.dir_name()

        # ensure there is an environment
        if 'env' not in kwargs:
            kwargs['env'] = {}

        # create environment variables for docker commands
        kwargs['env'].update({
            'COMPOSE_PROJECT_NAME': project.get_name(),
            'KIWI_HUB_NAME': config['network:name'],
            'CONFDIR': os.path.join(config['runtime:storage'], CONF_DIRECTORY_NAME),
            'TARGETDIR': project.target_dir_name()
        })

        logging.debug(f"kwargs updated: {kwargs}")

    return kwargs


class DockerCommand(Executable):
    __has_tried = False

    def __init__(self, exe_name):
        super().__init__(exe_name)

        if not DockerCommand.__has_tried:
            try:
                Executable('docker').run(
                    ['ps'],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                DockerCommand.__has_tried = True

            except subprocess.CalledProcessError:
                raise PermissionError("Cannot access docker, please get into the docker group or run as root!")

    def run(self, config, args, process_args, **kwargs):
        kwargs = _update_kwargs(**kwargs)

        # equivalent to 'super().run' but agnostic of nested class construct
        return super().__getattr__("run")(
            process_args, config,
            **kwargs
        )

    def run_less(self, config, args, process_args, **kwargs):
        kwargs = _update_kwargs(**kwargs)

        return super().__getattr__("run_less")(
            process_args, config,
            **kwargs
        )
