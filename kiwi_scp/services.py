from typing import List, Generator

import attr

from .service import Service
from .yaml import YAML


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
