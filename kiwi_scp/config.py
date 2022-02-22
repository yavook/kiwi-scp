import functools
from ipaddress import IPv4Network
from pathlib import Path
from typing import Optional, Dict, List, Any, TextIO, Tuple

from pydantic import BaseModel, constr, root_validator, validator

from ._constants import RE_SEMVER, RE_VARNAME, KIWI_CONF_NAME, RESERVED_PROJECT_NAMES
from .yaml import YAML


class InvalidFormatError(ValueError):
    """raised if format recognition unsuccessful"""

    cls: type
    member: Optional[str]
    data: str

    def __init__(self, cls, data, member = None):
        self.cls = cls
        self.data = data

        if member is not None:
            self.member = member
            super().__init__(f"Invalid {self.cls.__name__!r}.{self.member!r} Format: {self.data!r}")

        else:
            super().__init__(f"Invalid {self.cls.__name__!r} Format: {self.data!r}")


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
            raise InvalidFormatError(cls, str(values))


class ProjectNameReservedError(ValueError):
    """raised if trying to create a project with a reserved name"""

    name: str

    def __init__(self, name):
        self.name = name
        super().__init__(f"Project name {self.name!r} is reserved!")


class ProjectConfig(BaseModel):
    """a project subsection"""

    name: constr(regex=RE_VARNAME)
    enabled: bool = True
    override_storage: Optional[StorageConfig]

    @property
    def kiwi_dict(self) -> Dict[str, Any]:
        """write this object as a dictionary of strings"""

        result = self.dict(exclude={"override_storage"})

        if self.override_storage is not None:
            result["override_storage"] = self.override_storage.kiwi_dict

        return result

    @validator("name")
    @classmethod
    def check_project(cls, value: str) -> str:
        """check if project name is allowed"""

        if value in RESERVED_PROJECT_NAMES:
            raise ProjectNameReservedError(value)

        return value

    @validator("override_storage", pre=True)
    @classmethod
    def unify_storage(cls, value) -> Dict[str, Any]:
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
            raise InvalidFormatError(ProjectConfig, values)


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


class MissingMemberError(ValueError):
    """raised if class member is missing a definition"""

    cls: type
    member: str

    def __init__(self, cls, member):
        self.cls = cls
        self.member = member
        super().__init__(f"Member {self.cls.__name__!r}.{self.member!r} is required!")


class KiwiConfig(BaseModel):
    """represents a kiwi.yml"""

    version: constr(regex=RE_SEMVER) = "0.2.1"

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
    def from_directory(cls, directory: Path) -> "KiwiConfig":
        """parses an actual kiwi.yml from disk (cached)"""

        try:
            with open(directory.joinpath(KIWI_CONF_NAME)) as kc:
                return cls.parse_obj(YAML().load(kc))

        except FileNotFoundError:
            # return the defaults if no kiwi.yml found
            return cls.from_default()

    @classmethod
    @functools.lru_cache(maxsize=1)
    def from_default(cls) -> "KiwiConfig":
        """returns the default config (cached)"""

        return cls()

    def get_project_config(self, name: str) -> Optional[ProjectConfig]:
        """returns the config of a project with a given name"""

        for project in self.projects:
            if project.name == name:
                return project

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

    def dump_kiwi_yml(self, stream: TextIO = None) -> Optional[str]:
        """dump a kiwi.yml file"""

        return YAML().dump_kiwi_yml(self.kiwi_dict, stream=stream)

    @property
    def kiwi_yml(self) -> str:
        """get a kiwi.yml dump as a string"""

        return self.dump_kiwi_yml()

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
                raise InvalidFormatError(KiwiConfig, value, "shells")

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
                            raise InvalidFormatError(KiwiConfig, value, "projects")

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
                raise InvalidFormatError(KiwiConfig, value, "projects")

    @validator("environment", pre=True)
    @classmethod
    def unify_environment(cls, value) -> Dict[str, Optional[str]]:
        """parse different environment notations"""

        def parse_str(var_val: Any) -> Tuple[str, Optional[str]]:
            """parse a "<variable>=<value>" string"""

            try:
                idx = str(var_val).find("=")
            except Exception:
                # undefined format
                raise InvalidFormatError(KiwiConfig, value, "environment")

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
    def unify_storage(cls, value) -> Dict[str, Any]:
        """parse different storage notations"""

        if value is None:
            # empty storage
            raise MissingMemberError(KiwiConfig, "storage")

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
    def unify_network(cls, value) -> Dict[str, Any]:
        """parse different network notations"""

        if value is None:
            # empty network
            raise MissingMemberError(KiwiConfig, "network")

        elif isinstance(value, dict):
            # native dict format
            return value

        else:
            # undefined format
            raise InvalidFormatError(KiwiConfig, value, "network")
