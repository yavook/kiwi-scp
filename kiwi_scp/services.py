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
        path_str_list = TypeVar("path_str_list", Union[Path, str], List[Union[Path, str]])

        def prefix_path(path: path_str_list, prefix: Path) -> path_str_list:
            if isinstance(path, Path):
                return prefix.absolute().joinpath(path)

            elif isinstance(path, str):
                return prefix_path(Path(path), prefix)

            elif isinstance(path, list):
                return [prefix_path(p, prefix) for p in path]

        project = self.parent_project

        if project is None:
            return

        instance = project.parent_instance
        cfgs = list(self.configs)

        local_cfgs = prefix_path(cfgs, instance.config_directory)
        storage_cfgs = prefix_path(cfgs, instance.storage_config_directory)
        storage_dirs = [path.parent for path in storage_cfgs]

        Rootkit("rsync").run([
            "mkdir", "-p", storage_dirs
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        Rootkit("rsync").run([
            "rsync", "-rpt", list(zip(local_cfgs, storage_cfgs))
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
