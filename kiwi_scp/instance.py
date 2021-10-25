import functools
import re
from pathlib import Path
from typing import List, Dict, Any, Generator

import attr
import click
import yaml

from ._constants import COMPOSE_FILE_NAME
from .config import Config

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
class Project:
    directory: Path = attr.ib()
    services: List[Service] = attr.ib()

    @classmethod
    @functools.lru_cache(maxsize=10)
    def from_directory(cls, directory: Path):
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            yml = yaml.safe_load(cf)

        return cls(
            directory=directory,
            services=[
                Service.from_description(name, description)
                for name, description in yml["services"].items()
            ],
        )


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> Config:
        """shorthand: get the current configuration"""

        return Config.from_instance(self.directory)

    @property
    def projects(self) -> Generator[Project, None, None]:
        return (
            Project.from_directory(self.directory.joinpath(project.name))
            for project in self.config.projects
        )


pass_instance = click.make_pass_decorator(Instance, ensure=True)
