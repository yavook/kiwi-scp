import functools
import re
from pathlib import Path
from typing import List, Dict, Any, Generator

import attr
import click
from ruamel.yaml import YAML

from ._constants import COMPOSE_FILE_NAME
from .config import KiwiConfig, ProjectConfig

_RE_CONFDIR = re.compile(r"^\s*\$(?:CONFDIR|{CONFDIR})/+(.*)$", flags=re.UNICODE)


@attr.s
class Service:
    name: str = attr.ib()
    configs: List[Path] = attr.ib()

    @classmethod
    def from_description(cls, name: str, description: Dict[str, Any]):
        configs: List[Path] = []

        if "volumes" in description:
            volumes: List[str] = description["volumes"]

            for volume in volumes:
                host_part = volume.split(":")[0]
                confdir = _RE_CONFDIR.match(host_part)

                if confdir:
                    configs.append(Path(confdir.group(1)))

        return cls(
            name=name,
            configs=configs,
        )


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> KiwiConfig:
        """shorthand: get the current configuration"""

        return KiwiConfig.from_directory(self.directory)

    @classmethod
    @functools.lru_cache(maxsize=10)
    def _parse_compose_file(cls, directory: Path):
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            yml = YAML()
            return yml.load(cf)

    def get_services(self, project_name: str) -> Generator[Service, None, None]:
        yml = Instance._parse_compose_file(self.directory.joinpath(project_name))

        return (
            Service.from_description(name, description)
            for name, description in yml["services"].items()
        )


pass_instance = click.make_pass_decorator(Instance, ensure=True)
