# system
import logging
import os
import subprocess

# parent
from ..._constants import KIWI_ROOT

# local
from .dockercommand import DockerCommand


def _prefix_path(prefix, path):
    abs_path = os.path.abspath(path)
    return os.path.realpath(prefix + '/' + abs_path)


def prefix_path(path):
    if isinstance(path, str):
        return _prefix_path('/mnt/', path)
    elif isinstance(path, list):
        return [_prefix_path('/mnt/', p) for p in path]


def _image_name(image_tag):
    if image_tag is not None:
        return f"kiwi-config/auxiliary:{image_tag}"
    else:
        return "alpine:latest"


class Rootkit:
    class __Rootkit:
        __image_tag = None

        def __init__(self, image_tag=None):
            self.__image_tag = image_tag

        def __exists(self, config, args):
            ps = DockerCommand('docker').run(
                config, args, [
                    'images',
                    '--filter', f"reference={_image_name(self.__image_tag)}",
                    '--format', '{{.Repository}}:{{.Tag}}'
                ],
                stdout=subprocess.PIPE
            )

            return str(ps.stdout, 'utf-8').strip() == _image_name(self.__image_tag)

        def __build_image(self, config, args):
            if self.__exists(config, args):
                logging.info(f"Using image {_image_name(self.__image_tag)}")
            else:
                if self.__image_tag is None:
                    logging.info(f"Pulling image {_image_name(self.__image_tag)}")
                    DockerCommand('docker').run(
                        config, args, ['pull', _image_name(self.__image_tag)],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )

                else:
                    logging.info(f"Building image {_image_name(self.__image_tag)}")
                    DockerCommand('docker').run(
                        config, args,
                        [
                            'build',
                            '-t', _image_name(self.__image_tag),
                            '-f', f"{KIWI_ROOT}/images/{self.__image_tag}.Dockerfile",
                            f"{KIWI_ROOT}/images"
                        ],
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                    )

        def run(self, config, args, process_args, **kwargs):
            self.__build_image(config, args)
            DockerCommand('docker').run(
                config, args,
                [
                    'run', '--rm',
                    '-v', '/:/mnt',
                    '-u', 'root',
                    _image_name(self.__image_tag),
                    *process_args
                ],
                **kwargs
            )

    __image_tag = None
    __instances = {}

    def __init__(self, image_tag=None):
        self.__image_tag = image_tag

        if _image_name(self.__image_tag) not in Rootkit.__instances:
            Rootkit.__instances[_image_name(self.__image_tag)] = Rootkit.__Rootkit(image_tag)

    def __getattr__(self, item):
        return getattr(self.__instances[_image_name(self.__image_tag)], item)
