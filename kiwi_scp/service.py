import re
import subprocess
from pathlib import Path
from typing import Generator

import attr
from ruamel.yaml import CommentedMap

from .executable import COMPOSE_EXE
from .project import Project


@attr.s
class Service:
    name: str = attr.ib()
    content: CommentedMap = attr.ib()
    parent: "Project" = attr.ib()

    _RE_CONFDIR = re.compile(r"^\s*\$(?:CONFDIR|{CONFDIR})/+(.*)$", flags=re.UNICODE)

    @property
    def configs(self) -> Generator[Path, None, None]:
        if "volumes" not in self.content:
            return

        for volume in self.content["volumes"]:
            host_part = volume.split(":")[0]
            cd_match = Service._RE_CONFDIR.match(host_part)

            if cd_match:
                yield Path(cd_match.group(1))

    def has_executable(self, exe_name: str) -> bool:
        try:
            # test if desired executable exists
            COMPOSE_EXE.run(
                ["exec", "-T", self.name, "/bin/sh", "-c", f"command -v {exe_name}"],
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                **self.parent.process_kwargs,
            )
            return True

        except subprocess.CalledProcessError:
            return False