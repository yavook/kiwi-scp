import functools
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Dict, Any

import attr
from ruamel.yaml import CommentedMap

from ._constants import COMPOSE_FILE_NAME, CONFIG_DIRECTORY_NAME
from .config import ProjectConfig
from .service import Service
from .services import Services
from .yaml import YAML

if TYPE_CHECKING:
    from .instance import Instance


@attr.s
class Project:
    directory: Path = attr.ib()
    parent_instance: "Instance" = attr.ib()

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
        return self.parent_instance.config.get_project_config(self.name)

    @property
    def process_kwargs(self) -> Dict[str, Any]:
        directory: Path = self.directory
        project_name: str = self.name
        kiwi_hub_name: str = self.parent_instance.config.network.name
        kiwi_instance_dir: Path = self.parent_instance.config.storage.directory
        kiwi_config_dir: Path = kiwi_instance_dir.joinpath(CONFIG_DIRECTORY_NAME)
        kiwi_project_dir: Path = kiwi_instance_dir.joinpath(project_name)

        if self.config.override_storage is not None:
            kiwi_project_dir = self.config.override_storage.directory

        result: Dict[str, Any] = {
            "cwd": str(directory),
            "env": {
                "COMPOSE_PROJECT_NAME": project_name,
                "KIWI_HUB_NAME": kiwi_hub_name,
                "KIWI_INSTANCE": str(kiwi_instance_dir),
                "KIWI_CONFIG": str(kiwi_config_dir),
                "KIWI_PROJECT": str(kiwi_project_dir),
            },
        }

        result["env"].update(self.parent_instance.config.environment)

        return result

    @property
    def services(self) -> Services:
        yml = Project._parse_compose_file(self.directory)

        return Services([
            Service(
                name=name,
                content=content,
                parent_project=self,
            ) for name, content in yml["services"].items()
        ])
