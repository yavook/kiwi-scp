from pathlib import Path
from typing import Generator

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
