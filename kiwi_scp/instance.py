import functools
import re
from pathlib import Path
from typing import Generator, List, Tuple, Optional

import attr
from ruamel.yaml.comments import CommentedMap

from ._constants import COMPOSE_FILE_NAME
from .config import KiwiConfig
from .misc import YAML

_RE_CONFDIR = re.compile(r"^\s*\$(?:CONFDIR|{CONFDIR})/+(.*)$", flags=re.UNICODE)


@attr.s
class Service:
    name: str = attr.ib()
    content: CommentedMap = attr.ib()

    @property
    def configs(self) -> Generator[Path, None, None]:
        if "volumes" not in self.content:
            return

        for volume in self.content["volumes"]:
            host_part = volume.split(":")[0]
            cd_match = _RE_CONFDIR.match(host_part)

            if cd_match:
                yield Path(cd_match.group(1))


@attr.s
class Services:
    content: List[Service] = attr.ib()

    def __str__(self) -> str:
        return YAML().dump({
            "services": {
                service.name: service.content
                for service in self.content
            }
        }).strip()

    def __bool__(self) -> bool:
        return bool(self.content)

    def filter_existing(self, service_names: List[str]):
        return Services([
            service
            for service in self.content
            if service.name in service_names
        ])


@attr.s
class Project:
    directory: Path = attr.ib()

    @staticmethod
    @functools.lru_cache(maxsize=10)
    def _parse_compose_file(directory: Path) -> CommentedMap:
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            return YAML().load(cf)

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def services(self) -> Services:
        yml = Project._parse_compose_file(self.directory)

        return Services([
            Service(name, description)
            for name, description in yml["services"].items()
        ])


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> KiwiConfig:
        """shorthand: get the current configuration"""

        return KiwiConfig.from_directory(self.directory)

    def get_project(self, project_name: str) -> Optional[Project]:
        for project in self.config.projects:
            if project.name == project_name:
                return Project(self.directory.joinpath(project.name))
