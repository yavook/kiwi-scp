import functools
import re
from pathlib import Path
from typing import Generator, List, Optional, Dict, Any

import attr
from ruamel.yaml.comments import CommentedMap

from ._constants import COMPOSE_FILE_NAME, CONF_DIRECTORY_NAME
from .config import KiwiConfig, ProjectConfig
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

    def filter_existing(self, service_names: List[str]) -> "Services":
        return Services([
            service
            for service in self.content
            if service.name in service_names
        ])


@attr.s
class Project:
    directory: Path = attr.ib()
    config: KiwiConfig = attr.ib()

    @staticmethod
    @functools.lru_cache(maxsize=10)
    def _parse_compose_file(directory: Path) -> CommentedMap:
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            return YAML().load(cf)

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def project_config(self) -> ProjectConfig:
        return self.config.get_project_config(self.name)

    @property
    def process_kwargs(self) -> Dict[str, Any]:
        directory: Path = self.directory
        project_name: str = self.name
        kiwi_hub_name: str = self.config.network.name
        target_root_dir: Path = self.config.storage.directory
        conf_dir: Path = target_root_dir.joinpath(CONF_DIRECTORY_NAME)
        target_dir: Path = target_root_dir.joinpath(project_name)

        result: Dict[str, Any] = {
            "cwd": str(directory),
            "env": {
                "COMPOSE_PROJECT_NAME": project_name,
                "KIWI_HUB_NAME": kiwi_hub_name,
                "TARGETROOT": str(target_root_dir),
                "CONFDIR": str(conf_dir),
                "TARGETDIR": str(target_dir),
            },
        }

        result["env"].update(self.config.environment)

        return result

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

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __get_project(instance_directory: Path, project_name: str) -> Optional[Project]:
        instance = Instance(instance_directory)
        config = instance.config

        for project in config.projects:
            if project.name == project_name:
                return Project(
                    directory=instance_directory.joinpath(project.name),
                    config=config,
                )

    def get_project(self, project_name: str) -> Optional[Project]:
        project = Instance.__get_project(self.directory, project_name)
        if project is None:
            return

        project.instance = self
        return project
