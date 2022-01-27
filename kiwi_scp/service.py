import logging
import re
import subprocess
from itertools import zip_longest
from pathlib import Path
from typing import TYPE_CHECKING, Generator, Sequence

import attr
from ruamel.yaml import CommentedMap

from .executable import COMPOSE_EXE

if TYPE_CHECKING:
    from .instance import Instance
    from .project import Project

_logger = logging.getLogger(__name__)


@attr.s
class Service:
    name: str = attr.ib()
    content: CommentedMap = attr.ib()
    parent_project: "Project" = attr.ib()

    _RE_CONFIGDIR = re.compile(r"^\s*\$(?:CONFIGDIR|{CONFIGDIR})/+(.*)$", flags=re.UNICODE)

    @property
    def parent_instance(self) -> "Instance":
        return self.parent_project.parent_instance

    @property
    def configs(self) -> Generator[Path, None, None]:
        if "volumes" not in self.content:
            return

        for volume in self.content["volumes"]:
            host_part = volume.split(":")[0]
            cd_match = Service._RE_CONFIGDIR.match(host_part)

            if cd_match:
                yield Path(cd_match.group(1))

    def has_executable(self, exe_name: str) -> bool:
        try:
            # test if desired executable exists
            COMPOSE_EXE.run(
                ["exec", "-T", self.name, "/bin/sh", "-c", f"command -v {exe_name}"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                **self.parent_project.process_kwargs,
            )
            return True

        except subprocess.CalledProcessError:
            return False

    def existing_executables(self, exe_names: Sequence[str]) -> Generator[str, None, None]:
        for cur, nxt in zip_longest(exe_names, exe_names[1:]):
            if self.has_executable(cur):
                # found working shell
                _logger.debug(f"Found executable '{cur}'")
                yield cur

            elif nxt is not None:
                # try next in list
                _logger.info(f"Executable '{cur}' not found in container, trying '{nxt}'")

