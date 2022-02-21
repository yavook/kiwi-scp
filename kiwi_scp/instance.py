import logging
import subprocess
from pathlib import Path
from typing import Generator, Dict, Sequence

import attr

from ._constants import KIWI_CONF_NAME, CONFIG_DIRECTORY_NAME
from .config import KiwiConfig
from .executable import DOCKER_EXE
from .project import Project

_logger = logging.getLogger(__name__)


@attr.s
class Instance:
    directory: Path = attr.ib(default=Path('.'))

    @property
    def config(self) -> KiwiConfig:
        """shorthand: get the current configuration"""

        return KiwiConfig.from_directory(self.directory)

    def save_config(self, config: KiwiConfig) -> None:
        with open(self.directory.joinpath(KIWI_CONF_NAME), "w") as file:
            config.dump_kiwi_yml(file)

    @property
    def config_directory(self):
        return self.directory.joinpath(CONFIG_DIRECTORY_NAME)

    @property
    def storage_config_directory(self):
        return self.config.storage.directory.joinpath(CONFIG_DIRECTORY_NAME)

    @staticmethod
    def __find_net(net_name):
        ps = DOCKER_EXE.run([
            "network", "ls", "--filter", f"name={net_name}", "--format", "{{.Name}}"
        ], stdout=subprocess.PIPE)

        net_found = str(ps.stdout, 'utf-8').strip()

        return net_found == net_name

    def create_net(self):
        net_name = self.config.network.name
        net_cidr = str(self.config.network.cidr)

        if self.__find_net(net_name):
            _logger.info(f"Network '{net_name}' already exists")
            return

        try:
            DOCKER_EXE.run([
                "network", "create",
                "--driver", "bridge",
                "--internal",
                "--subnet", net_cidr,
                net_name
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _logger.info(f"Network '{net_name}' created")

        except subprocess.CalledProcessError:
            _logger.error(f"Error creating network '{net_name}'")

    def remove_net(self):
        net_name = self.config.network.name

        if not self.__find_net(net_name):
            _logger.info(f"Network '{net_name}' does not exist")
            return

        try:
            DOCKER_EXE.run([
                "network", "rm",
                net_name
            ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            _logger.info(f"Network '{net_name}' removed")

        except subprocess.CalledProcessError:
            _logger.error(f"Error removing network '{net_name}'")

    @property
    def projects(self) -> Generator[Project, None, None]:
        for project in self.config.projects:
            yield Project(
                directory=self.directory.joinpath(project.name),
                parent_instance=self,
            )

    def get_projects(self, project_names: Sequence[str]) -> Dict[str, Project]:
        existing_projects = {
            project.name: project
            for project in self.projects
            if project.name in project_names
        }
        nonexistent_projects = {
            name: None
            for name in project_names
            if name not in existing_projects
        }
        return {
            **existing_projects,
            **nonexistent_projects
        }
