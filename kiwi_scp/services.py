from pathlib import Path
from typing import List, Generator, Optional, TYPE_CHECKING

import attr

from .yaml import YAML

if TYPE_CHECKING:
    from .instance import Instance
    from .service import Service


@attr.s
class Services:
    content: List["Service"] = attr.ib()

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
    def parent_instance(self) -> Optional["Instance"]:
        if not self:
            return

        return self.content[0].parent_instance

    @property
    def configs(self) -> Generator[Path, None, None]:
        for service in self.content:
            yield from service.configs

    # def copy_configs(self) -> None:
    #     instance = self.parent_instance
    #
    #     if instance is None:
    #         return
    #
    #     print(list(self.configs))
    #
    #     # Rootkit("rsync").

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
