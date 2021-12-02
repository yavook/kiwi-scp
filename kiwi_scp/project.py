import functools
from pathlib import Path
from typing import Optional, Dict, Any

import attr
from ruamel.yaml import CommentedMap

from ._constants import COMPOSE_FILE_NAME, CONF_DIRECTORY_NAME
from .config import ProjectConfig
from .instance import Instance
from .service import Service
from .services import Services
from .yaml import YAML


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