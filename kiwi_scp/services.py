import subprocess
from pathlib import Path
from typing import List, Generator, Optional, TYPE_CHECKING, TypeVar, Union

import attr

from .rootkit import Rootkit
from .yaml import YAML

if TYPE_CHECKING:
    from .project import Project
    from .service import Service


@attr.s
class Services:
    content: List["Service"] = attr.ib()

    def __str__(self) -> str:
        return YAML().dump({
            "services": {
                service.name: service.content
                for service in self.content
            },
            "configs": [
                str(config)
                for config in self.configs
            ],
        }).strip()

    def __bool__(self) -> bool:
        return bool(self.content)

    @property
    def parent_project(self) -> Optional["Project"]:
        if not self:
            return

        return self.content[0].parent_project

    @property
    def configs(self) -> Generator[Path, None, None]:
        for service in self.content:
            yield from service.configs

    def copy_configs(self) -> None:
        project = self.parent_project
        configs = list(self.configs)

        if project is None or not configs:
            return

        instance = project.parent_instance

        Rootkit("rsync").run([
            "mkdir", "-p", instance.storage_directory
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        Rootkit("rsync").run([
            "rsync", "-rpt", instance.config_directory, instance.storage_directory
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

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
