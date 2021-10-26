import functools
import io
from ipaddress import IPv4Network
from pathlib import Path
from typing import Optional, Dict, List, Any, TextIO

from pydantic import BaseModel, constr, root_validator, validator
from ruamel.yaml import YAML

from ._constants import RE_SEMVER, RE_VARNAME, KIWI_CONF_NAME
from .misc import _format_kiwi_yml


class StorageConfig(BaseModel):
    """a storage subsection"""

    directory: Path

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        return {"directory": str(self.directory)}

    @root_validator(pre=True)
    @classmethod
    def unify_storage(cls, values) -> Dict[str, Any]:
        """parse different storage notations"""

        if "directory" in values:
            # default format
            return values

        else:
            # undefined format
            raise ValueError("Invalid Storage Format")


class ProjectConfig(BaseModel):
    """a project subsection"""

    name: constr(regex=RE_VARNAME)
    enabled: bool = True
    override_storage: Optional[StorageConfig]

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        if self.override_storage is None:
            return {self.name: self.enabled}

        else:
            result = self.dict(exclude={"override_storage"})
            result["override_storage"] = self.override_storage.kiwi_dict
            return result

    @validator("override_storage", pre=True)
    @classmethod
    def unify_storage(cls, value):
        """parse different storage notations"""

        if value is None or isinstance(value, dict):
            return value

        elif isinstance(value, str):
            return {"directory": value}

        elif isinstance(value, list) and len(value) == 1:
            return {"directory": value[0]}

        else:
            # undefined format
            return {}

    @root_validator(pre=True)
    @classmethod
    def unify_project(cls, values) -> Dict[str, Any]:
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
            raise ValueError("Invalid Project Format")


class NetworkConfig(BaseModel):
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


class KiwiConfig(BaseModel):
    """represents a kiwi.yml"""

    version: constr(regex=RE_SEMVER) = "0.2.0"

    shells: List[Path] = [
        Path("/bin/bash"),
    ]

    projects: List[ProjectConfig] = []

    environment: Dict[str, Optional[str]] = {}

    storage: StorageConfig = StorageConfig(
        directory="/var/local/kiwi",
    )

    network: NetworkConfig = NetworkConfig(
        name="kiwi_hub",
        cidr="10.22.46.0/24",
    )

    @classmethod
    @functools.lru_cache(maxsize=5)
    def from_directory(cls, directory: Path):
        """parses an actual kiwi.yml from disk (cached)"""

        try:
            with open(directory.joinpath(KIWI_CONF_NAME)) as kc:
                return cls.parse_obj(YAML().load(kc))

        except FileNotFoundError:
            # return the defaults if no kiwi.yml found
            return cls.from_default()

    @classmethod
    @functools.lru_cache(maxsize=1)
    def from_default(cls):
        """returns the default config (cached)"""

        return cls()

    def get_project_config(self, name: str) -> ProjectConfig:
        """returns the config of a project with a given name"""

        for project in self.projects:
            if project.name == name:
                return project

        raise ValueError("No Such Project")

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

    def dump_kiwi_yml(self, stream: TextIO) -> None:
        """dump a kiwi.yml file"""

        yml = YAML()
        yml.indent(offset=2)
        yml.dump(self.kiwi_dict, stream=stream, transform=_format_kiwi_yml)

    @property
    def kiwi_yml(self) -> str:
        """get a kiwi.yml dump as a string"""

        sio = io.StringIO()
        self.dump_kiwi_yml(sio)
        result: str = sio.getvalue()
        sio.close()

        return result

    @validator("shells", pre=True)
    @classmethod
    def unify_shells(cls, value) -> List[str]:
        """parse different shells notations"""

        if value is None:
            return []

        elif isinstance(value, list):
            return value

        elif isinstance(value, dict):
            return list(value)

        else:
            # any other format (try to coerce to str first)
            try:
                return [str(value)]

            except Exception:
                # undefined format
                raise ValueError("Invalid Shells Format")

    @validator("projects", pre=True)
    @classmethod
    def unify_projects(cls, value) -> List[Dict[str, str]]:
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
                        try:
                            # handle single project name
                            result.append({"name": str(entry)})

                        except Exception:
                            # undefined format
                            raise ValueError("Invalid Projects Format")

            return result

        elif isinstance(value, dict):
            # handle single project dict
            return [value]

        else:
            # any other format (try to coerce to str first)
            try:
                # handle as a single project name
                return [{"name": str(value)}]

            except Exception:
                # undefined format
                raise ValueError("Invalid Projects Format")

    @validator("environment", pre=True)
    @classmethod
    def unify_environment(cls, value) -> Dict[str, Optional[str]]:
        """parse different environment notations"""

        def parse_str(var_val: Any) -> (str, Optional[str]):
            """parse a "<variable>=<value>" string"""

            try:
                idx = str(var_val).find("=")
            except Exception:
                # undefined format
                raise ValueError("Invalid Environment Format")

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

        else:
            # any other format (try to coerce to str first)
            # string format (single variable):
            # "<var>=<value>"
            key, value = parse_str(value)
            return {key: value}

    @validator("storage", pre=True)
    @classmethod
    def unify_storage(cls, value):
        """parse different storage notations"""

        if value is None:
            # empty storage
            raise ValueError("No Storage Given")

        elif isinstance(value, dict):
            # native dict format
            return value

        elif isinstance(value, str):
            # just the directory string
            return {"directory": value}

        elif isinstance(value, list) and len(value) == 1 and isinstance(value[0], str):
            # directory string as a single-item list
            return {"directory": value[0]}

        else:
            # undefined format
            return {}

    @validator("network", pre=True)
    @classmethod
    def unify_network(cls, value):
        """parse different network notations"""

        if value is None:
            # empty network
            raise ValueError("No Network Given")

        elif isinstance(value, dict):
            # native dict format
            return value

        else:
            # undefined format
            raise ValueError("Invalid Network Format")
