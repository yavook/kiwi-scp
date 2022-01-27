import functools
import logging
import subprocess
from pathlib import Path
from typing import Optional, TypeVar, Union, Sequence, Any

import attr

from ._constants import IMAGES_DIRECTORY_NAME, LOCAL_IMAGES_NAME, DEFAULT_IMAGE_NAME
from .executable import DOCKER_EXE

_logger = logging.getLogger(__name__)

ROOTKIT_PREFIX = Path("/mnt")


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

    def run(self, process_args, **kwargs) -> Optional[subprocess.CompletedProcess]:
        any_sequence = TypeVar("any_sequence", Union[str, Path, Any], Sequence[Union[str, Path, Any]])

        def parse_args(argument: any_sequence) -> any_sequence:
            if isinstance(argument, str):
                return argument

            elif isinstance(argument, Path):
                if argument.is_absolute():
                    argument = argument.relative_to("/")

                return str(ROOTKIT_PREFIX.joinpath(argument))

            elif not isinstance(argument, Sequence):
                return str(argument)

            else:
                parsed = [parse_args(path) for path in argument]

                flat = []
                for item in parsed:
                    if not isinstance(item, list):
                        flat.append(item)
                    else:
                        flat.extend(item)

                return flat

        self.__build_image()
        return DOCKER_EXE.run([
            "run", "--rm",
            "-v", f"/:{ROOTKIT_PREFIX!s}",
            "-u", "root",
            Rootkit.__image_name(self.image_tag),
            *parse_args(process_args)
        ], **kwargs)
