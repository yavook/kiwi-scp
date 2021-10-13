from ipaddress import IPv4Network
from pathlib import Path
from typing import Optional, Dict, List

from pydantic import BaseModel, constr, root_validator, validator

from ._constants import RE_SEMVER, RE_VARNAME


class _Storage(BaseModel):
    """a storage subsection"""

    directory: Path


class _Project(BaseModel):
    """a project subsection"""

    name: constr(
        regex=RE_VARNAME
    )
    enabled: bool = True
    override_storage: Optional[_Storage]

    @root_validator(pre=True)
    @classmethod
    def unify_project(cls, values):
        """parse different project notations"""

        if "name" in values:
            # default format
            return values

        elif len(values) == 1:
            # short format:
            # - <name>: <enabled>

            name, enabled = list(values.items())[0]
            return {
                "name": name,
                "enabled": True if enabled is None else enabled
            }

        else:
            # undefined format
            raise ValueError


class _Network(BaseModel):
    """a network subsection"""

    name: constr(to_lower=True, regex=RE_VARNAME)
    cidr: IPv4Network


class Config(BaseModel):
    """represents a kiwi.yml"""

    version: constr(regex=RE_SEMVER) = "0.2.0"

    shells: Optional[List[Path]] = [
        Path("/bin/bash"),
    ]

    environment: Dict[str, Optional[str]] = {}

    projects: Optional[List[_Project]]

    storage: _Storage = _Storage(
        directory="/var/local/kiwi",
    )

    network: _Network = _Network(
        name="kiwi_hub",
        cidr="10.22.46.0/24",
    )

    @validator("environment", pre=True)
    @classmethod
    def unify_environment(cls, value) -> Dict[str, Optional[str]]:
        """parse different environment notations"""

        def parse_str(var_val: str) -> (str, Optional[str]):
            """parse a "<variable>=<value>" string"""

            idx = var_val.find("=")
            if idx == -1:
                # don't split, just define the variable
                return var_val, None
            else:
                # split string, set variable to value
                return var_val[:idx], var_val[idx + 1:]

        if value is None:
            # empty environment
            return {}

        elif isinstance(value, dict):
            # native dict format
            return value

        elif isinstance(value, list):
            # list format (multiple strings)

            result: Dict[str, Optional[str]] = {}
            for item in value:
                key, value = parse_str(item)
                result[key] = value

            return result

        elif isinstance(value, str):
            # string format (single variable):
            # "<var>=<value>"

            key, value = parse_str(value)
            return {key: value}

        elif isinstance(value, int):
            # integer format (just define single oddly named variable)
            return {str(value): None}

        else:
            # undefined format
            raise ValueError
