import re
from ipaddress import IPv4Network
from pathlib import Path
from typing import Optional, Dict, List, Any

import yaml
from pydantic import BaseModel, constr, root_validator, validator

from ._constants import RE_SEMVER, RE_VARNAME, HEADER_KIWI_CONF_NAME


# indent yaml lists
class _KiwiDumper(yaml.Dumper):
    def increase_indent(self, flow=False, indentless=False):
        return super().increase_indent(flow, False)


class _Storage(BaseModel):
    """a storage subsection"""

    directory: Path

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        return {"directory": str(self.directory)}


class _Project(BaseModel):
    """a project subsection"""

    name: constr(regex=RE_VARNAME)
    enabled: bool = True
    override_storage: Optional[_Storage]

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        if self.override_storage is None:
            return {self.name: self.enabled}

        else:
            result = self.dict(exclude={"override_storage"})
            result["override_storage"] = self.override_storage.kiwi_dict
            return result

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
                "enabled": True if enabled is None else enabled,
            }

        else:
            # undefined format
            raise ValueError


class _Network(BaseModel):
    """a network subsection"""

    name: constr(to_lower=True, regex=RE_VARNAME)
    cidr: IPv4Network

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        return {
            "name": self.name,
            "cidr": str(self.cidr),
        }


class Config(BaseModel):
    """represents a kiwi.yml"""

    version: constr(regex=RE_SEMVER) = "0.2.0"

    shells: Optional[List[Path]] = [
        Path("/bin/bash"),
    ]

    projects: List[_Project] = []

    environment: Dict[str, Optional[str]] = {}

    storage: _Storage = _Storage(
        directory="/var/local/kiwi",
    )

    network: _Network = _Network(
        name="kiwi_hub",
        cidr="10.22.46.0/24",
    )

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        result = {
            "version": self.version,
            "shells": [str(shell) for shell in self.shells],
        }

        if self.projects:
            result["projects"] = [
                project.kiwi_dict
                for project in self.projects
            ]

        if self.environment:
            result["environment"] = self.environment

        result["storage"] = self.storage.kiwi_dict

        result["network"] = self.network.kiwi_dict

        return result

    @property
    def kiwi_yml(self) -> str:
        """dump a kiwi.yml file"""

        yml_string = yaml.dump(
            self.kiwi_dict,
            Dumper=_KiwiDumper,
            default_flow_style=False,
            sort_keys=False,
        )

        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # load header comment from file
        with open(HEADER_KIWI_CONF_NAME, 'r') as stream:
            yml_string = stream.read() + yml_string

        return yml_string

    @validator("projects", pre=True)
    @classmethod
    def unify_projects(cls, value):
        """parse different projects notations"""

        if value is None:
            # empty projects list
            return []

        elif isinstance(value, list):
            # handle projects list

            result = []
            for entry in value:
                # ignore empties
                if entry is not None:
                    if isinstance(entry, dict):
                        # handle single project dict
                        result.append(entry)

                    else:
                        # handle single project name
                        result.append({"name": str(entry)})

            return result

        elif isinstance(value, dict):
            # handle single project dict
            return [value]

        else:
            # handle single project name
            return [{"name": str(value)}]

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
                key, value = parse_str(str(item))
                result[key] = value

            return result

        elif isinstance(value, str):
            # string format (single variable):
            # "<var>=<value>"

            key, value = parse_str(value)
            return {key: value}

        else:
            # any other format (try to coerce to str first)
            try:
                key, value = parse_str(str(value))
                return {key: value}

            except Exception as e:
                # undefined format
                raise ValueError("Invalid Environment Format")
