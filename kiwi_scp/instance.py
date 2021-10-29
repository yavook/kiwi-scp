import functools
import re
from pathlib import Path
from typing import Generator, List, Tuple, Optional

import attr
import click
from ruamel.yaml.comments import CommentedMap

from ._constants import COMPOSE_FILE_NAME
from .config import KiwiConfig
from .misc import YAML

_RE_CONFDIR = re.compile(r"^\s*\$(?:CONFDIR|{CONFDIR})/+(.*)$", flags=re.UNICODE)


@attr.s
class Service:
    name: str = attr.ib()
    description: CommentedMap = attr.ib()

    def __str__(self) -> str:
        return YAML().dump({
            "service": {
                self.name: self.description
            }
        }).strip()

    @property
    def configs(self) -> Generator[Path, None, None]:
        if "volumes" not in self.description:
            return

        for volume in self.description["volumes"]:
            host_part = volume.split(":")[0]
            cd_match = _RE_CONFDIR.match(host_part)

            if cd_match:
                yield Path(cd_match.group(1))


@attr.s
class Services:
    project_name: str = attr.ib()
    content: List[Service] = attr.ib()

    def __str__(self) -> str:
        return YAML().dump({
            "services": {
                service.name: service.description
                for service in self.content
            }
        }).strip()


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> KiwiConfig:
        """shorthand: get the current configuration"""

        return KiwiConfig.from_directory(self.directory)

    @staticmethod
    @functools.lru_cache(maxsize=10)
    def _parse_compose_file(directory: Path):
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            return YAML().load(cf)

    def get_services(self, project_name: str, service_names: Optional[Tuple[str]] = None) -> Services:
        yml = Instance._parse_compose_file(self.directory.joinpath(project_name))
        services = [
            Service(name, description)
            for name, description in yml["services"].items()
        ]

        if not service_names:
            return Services(project_name, services)
        else:
            return Services(project_name, [
                service
                for service in services
                if service.name in service_names
            ])
