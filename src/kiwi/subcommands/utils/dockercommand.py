# system
import logging
import os
import subprocess

# local
from .executable import Executable
from .project import *


def _update_kwargs(config, args, **kwargs):
    # project given in args: command affects a project in this instance
    project_name = get_project_name(args)
    if project_name is not None:
        # execute command in project directory
        kwargs['cwd'] = get_project_dir(config, project_name)

        # ensure there is an environment
        if 'env' not in kwargs:
            kwargs['env'] = {}

        # create environment variables for docker commands
        kwargs['env'].update({
            'COMPOSE_PROJECT_NAME': project_name,
            'KIWI_HUB_NAME': config['network:name'],
            'CONFDIR': os.path.join(config['runtime:storage'], 'conf'),
            'TARGETDIR': os.path.join(config['runtime:storage'], get_project_dir(config, project_name))
        })

        logging.debug(f"kwargs updated: {kwargs}")

    return kwargs


class DockerCommand(Executable):
    __requires_root = None

    def __init__(self, exe_name):
        super().__init__(exe_name)

        if DockerCommand.__requires_root is None:
            try:
                Executable('docker').run(
                    ['ps'],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                DockerCommand.__requires_root = False
            except subprocess.CalledProcessError:
                DockerCommand.__requires_root = True

    def run(self, config, args, process_args, **kwargs):
        kwargs = _update_kwargs(config, args, **kwargs)

        # equivalent to 'super().run' but agnostic of nested class construct
        return super().__getattr__("run")(
            process_args, config, DockerCommand.__requires_root,
            **kwargs
        )

    def run_less(self, config, args, process_args, **kwargs):
        kwargs = _update_kwargs(config, args, **kwargs)

        return super().__getattr__("run_less")(
            process_args, config, DockerCommand.__requires_root,
            **kwargs
        )
