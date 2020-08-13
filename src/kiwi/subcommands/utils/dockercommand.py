# system
import logging
import os
import subprocess

# local
from .executable import Executable


def _update_kwargs(config, args, **kwargs):
    project_name = args.project
    project_marker = config['markers:project']
    project_dir = f'{project_name}{project_marker}'
    kwargs['cwd'] = project_dir

    if 'env' not in kwargs:
        kwargs['env'] = {}

    if config['runtime:env'] is not None:
        kwargs['env'].update(config['runtime:env'])

    kwargs['env'].update({
        'KIWI_HUB_NAME': config['network:name'],
        'COMPOSE_PROJECT_NAME': project_name,
        'CONFDIR': os.path.join(config['runtime:storage'], 'conf'),
        'TARGETDIR': os.path.join(config['runtime:storage'], project_dir)
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
        super().__getattr__("run")(
            process_args, DockerCommand.__requires_root,
            **kwargs
        )

    def run_less(self, config, args, process_args, **kwargs):
        kwargs = _update_kwargs(config, args, **kwargs)

        super().__getattr__("run_less")(
            process_args, DockerCommand.__requires_root,
            **kwargs
        )
