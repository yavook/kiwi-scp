# system
import logging
import os
import subprocess

# local
from .executable import Executable


def _update_kwargs(config, args, **kwargs):
    if args is not None and 'projects' in args and args.projects is not None:
        # command affects a project in this instance

        project_name = args.projects
        if isinstance(project_name, list) and len(project_name) > 0:
            project_name = project_name[0]

        project_marker = config['markers:project']
        project_dir = f'{project_name}{project_marker}'
        kwargs['cwd'] = project_dir

        if 'env' not in kwargs:
            kwargs['env'] = {}

        kwargs['env'].update({
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
