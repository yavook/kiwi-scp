from pathlib import Path
from typing import Generator, Dict, Sequence

import attr

from .config import KiwiConfig
from .project import Project


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
