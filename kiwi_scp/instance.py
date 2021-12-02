import functools
import re
import subprocess
from pathlib import Path
from typing import Generator, List, Optional, Dict, Any

import attr
from ruamel.yaml.comments import CommentedMap

from ._constants import COMPOSE_FILE_NAME, CONF_DIRECTORY_NAME
from .config import KiwiConfig, ProjectConfig
from .executable import COMPOSE_EXE
from .misc import YAML


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

    @property
    def names(self) -> Generator[str, None, None]:
        return (
            service.name
            for service in self.content
        )

    def filter_existing(self, service_names: List[str]) -> "Services":
        return Services([
            service
            for service in self.content
            if service.name in service_names
        ])


@attr.s
class Project:
    directory: Path = attr.ib()
    parent: "Instance" = attr.ib()

    @staticmethod
    @functools.lru_cache(maxsize=10)
    def _parse_compose_file(directory: Path) -> CommentedMap:
        with open(directory.joinpath(COMPOSE_FILE_NAME), "r") as cf:
            return YAML().load(cf)

    @property
    def name(self) -> str:
        return self.directory.name

    @property
    def config(self) -> Optional[ProjectConfig]:
        return self.parent.config.get_project_config(self.name)

    @property
    def process_kwargs(self) -> Dict[str, Any]:
        directory: Path = self.directory
        project_name: str = self.name
        kiwi_hub_name: str = self.parent.config.network.name
        target_root_dir: Path = self.parent.config.storage.directory
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

        result["env"].update(self.parent.config.environment)

        return result

    @property
    def services(self) -> Services:
        yml = Project._parse_compose_file(self.directory)

        return Services([
            Service(
                name=name,
                content=content,
                parent=self,
            ) for name, content in yml["services"].items()
        ])


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> KiwiConfig:
        """shorthand: get the current configuration"""

        return KiwiConfig.from_directory(self.directory)

    @property
    def projects(self) -> Generator[Project, None, None]:
        for project in self.config.projects:
            yield Project(
                directory=self.directory.joinpath(project.name),
                parent=self,
            )
