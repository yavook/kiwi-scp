import re
from typing import Optional, Dict, List

import pydantic


class _Storage(pydantic.BaseModel):
    """a storage subsection"""

    directory: str


class _Project(pydantic.BaseModel):
    """a project subsection"""

    name: str
    enabled: bool = True
    storage: Optional[_Storage]

    @pydantic.root_validator(pre=True)
    @classmethod
    def check_grammar(cls, values):
        if isinstance(values, dict):
            if "name" in values:
                return values

            elif len(values) == 1:
                name, enabled = list(values.items())[0]
                return {"name": name, "enabled": True if enabled is None else enabled}

        elif isinstance(values, str):
            return {"name": values}


class _Network(pydantic.BaseModel):
    """a network subsection"""

    name: str
    cidr: str


class Config(pydantic.BaseModel):
    """represents a kiwi.yml"""

    version: str
    shells: Optional[List[str]]
    environment: Optional[Dict[str, Optional[str]]]

    projects: Optional[List[_Project]]
    storage: _Storage
    network: _Network

    @pydantic.validator("version")
    @classmethod
    def check_version(cls, value: str) -> str:
        if not re.match(r"^[0-9]+(\.[0-9]+(\.[0-9]+)?)?$", value):
            raise ValueError

        return value

    @pydantic.validator("environment", pre=True)
    @classmethod
    def unify_env(cls, value) -> Optional[Dict[str, Optional[str]]]:
        if isinstance(value, dict):
            return value
        elif isinstance(value, list):
            result: Dict[str, Optional[str]] = {}
            for item in value:
                idx = item.find("=")
                if idx == -1:
                    key, value = item, None
                else:
                    key, value = item[:idx], item[idx + 1:]

                result[key] = value

            return result
        else:
            return None
