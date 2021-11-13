import functools
import logging
import subprocess
from pathlib import Path
from typing import Optional, TypeVar, Union, List

import attr

from ._constants import IMAGES_DIRECTORY_NAME, LOCAL_IMAGES_NAME, DEFAULT_IMAGE_NAME
from .executable import DOCKER_EXE

_logger = logging.getLogger(__name__)

PSL = TypeVar("PSL", Union[Path, str], List[Union[Path, str]])


def prefix_path(path: PSL, prefix: Path = Path("/mnt")) -> PSL:
    if isinstance(path, Path):
        return prefix.joinpath(path.absolute())

    if isinstance(path, str):
        return prefix_path(Path(path), prefix)

    elif isinstance(path, list):
        return [prefix_path(prefix, p) for p in path]


@attr.s
class Rootkit:
    image_tag: str = attr.ib()

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __image_name(image_tag: Optional[str]) -> str:
        if image_tag is not None:
            return f"{LOCAL_IMAGES_NAME}:{image_tag}"
        else:
            return DEFAULT_IMAGE_NAME

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __exists(image_tag: str) -> bool:
        ps = DOCKER_EXE.run([
            'images',
            '--filter', f"reference={Rootkit.__image_name(image_tag)}",
            '--format', '{{.Repository}}:{{.Tag}}'
        ], stdout=subprocess.PIPE)

        return str(ps.stdout, 'utf-8').strip() == Rootkit.__image_name(image_tag)

    def __build_image(self) -> None:
        if Rootkit.__exists(self.image_tag):
            _logger.info(f"Using image {Rootkit.__image_name(self.image_tag)}")
        else:
            if self.image_tag is None:
                _logger.info(f"Pulling image {Rootkit.__image_name(self.image_tag)}")
                DOCKER_EXE.run([
                    'pull', Rootkit.__image_name(self.image_tag)
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            else:
                _logger.info(f"Building image {Rootkit.__image_name(self.image_tag)}")
                DOCKER_EXE.run([
                    'build',
                    '-t', Rootkit.__image_name(self.image_tag),
                    '-f', f"{IMAGES_DIRECTORY_NAME}/{self.image_tag}.Dockerfile",
                    f"{IMAGES_DIRECTORY_NAME}"
                ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run(self, process_args, **kwargs):
        self.__build_image()
        DOCKER_EXE.run([
            'run', '--rm',
            '-v', '/:/mnt',
            '-u', 'root',
            Rootkit.__image_name(self.image_tag),
            *process_args
        ], **kwargs)
