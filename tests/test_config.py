from ipaddress import IPv4Network
from pathlib import Path

import pytest
import toml
from pydantic import ValidationError

from kiwi_scp.config import Config


class UnCoercible:
    """A class that doesn't have a string representation"""

    def __str__(self):
        raise ValueError


def test_default():
    c = Config()
    version = toml.load("./pyproject.toml")["tool"]["poetry"]["version"]

    assert c == Config.from_default()

    assert c.version == version
    assert len(c.shells) == 1
    assert c.shells[0] == Path("/bin/bash")
    assert c.projects == []
    assert c.environment == {}
    assert c.storage.directory == Path("/var/local/kiwi")
    assert c.network.name == "kiwi_hub"
    assert c.network.cidr == IPv4Network("10.22.46.0/24")


#########
# VERSION
#########

def test_version_valid():
    c = Config(version="0.0.0")

    assert c.version == "0.0.0"

    c = Config(version="0.0")

    assert c.version == "0.0"

    c = Config(version="0")

    assert c.version == "0"

    c = Config(version=1.0)

    assert c.version == "1.0"

    c = Config(version=1)

    assert c.version == "1"


def test_version_invalid():
    # definitely not a version
    with pytest.raises(ValidationError) as exc_info:
        Config(version="dnaf")

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"].find("string does not match regex") != -1
    assert error["type"] == "value_error.str.regex"

    # barely a version
    with pytest.raises(ValidationError) as exc_info:
        c = Config(version="0.0.0alpha")
        print(c.version)

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"].find("string does not match regex") != -1
    assert error["type"] == "value_error.str.regex"


########
# SHELLS
########

def test_shells_empty():
    c = Config(shells=None)

    assert c == Config(shells=[])

    assert c.shells == []


def test_shells_list():
    c = Config(shells=["/bin/sh", "sh"])

    assert len(c.shells) == 2
    assert c.shells[0] == Path("/bin/sh")
    assert c.shells[1] == Path("sh")

    c = Config(shells=["/bin/bash"])

    assert len(c.shells) == 1
    assert c.shells[0] == Path("/bin/bash")


def test_shells_dict():
    c = Config(shells={"/bin/bash": None})

    assert len(c.shells) == 1
    assert c.shells[0] == Path("/bin/bash")


def test_shells_coercible():
    c = Config(shells="/bin/bash")

    assert c == Config(shells=Path("/bin/bash"))

    assert len(c.shells) == 1
    assert c.shells[0] == Path("/bin/bash")

    c = Config(shells=123)

    assert len(c.shells) == 1
    assert c.shells[0] == Path("123")


def test_shells_uncoercible():
    with pytest.raises(ValidationError) as exc_info:
        Config(shells=UnCoercible())

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Shells Format"
    assert error["type"] == "value_error"

    with pytest.raises(ValidationError) as exc_info:
        Config(shells=["/bin/bash", UnCoercible()])

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "value is not a valid path"
    assert error["type"] == "type_error.path"


##########
# PROJECTS
##########

def test_proj_empty():
    c = Config(projects=None)

    assert c == Config(projects=[])

    assert c.projects == []


def test_proj_long():
    c = Config(projects=[{
        "name": "project",
        "enabled": False,
        "override_storage": {"directory": "/test/directory"},
    }])

    assert len(c.projects) == 1
    p = c.projects[0]
    assert p.name == "project"
    assert not p.enabled
    assert p.override_storage is not None
    assert p.override_storage.directory == Path("/test/directory")


def test_proj_short():
    c = Config(projects=[{
        "project": False,
    }])

    assert len(c.projects) == 1
    p = c.projects[0]
    assert p.name == "project"
    assert not p.enabled
    assert p.override_storage is None


def test_proj_dict():
    c = Config(projects={"name": "project"})

    assert c == Config(projects=[{"name": "project"}])

    assert len(c.projects) == 1
    p = c.projects[0]
    assert p.name == "project"
    assert p.enabled
    assert p.override_storage is None


def test_proj_invalid_dict():
    with pytest.raises(ValidationError) as exc_info:
        Config(projects={
            "random key 1": "random value 1",
            "random key 2": "random value 2",
        })

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Project Format"
    assert error["type"] == "value_error"


def test_proj_coercible():
    c = Config(projects="project")

    assert c == Config(projects=["project"])

    assert len(c.projects) == 1
    p = c.projects[0]
    assert p.name == "project"
    assert p.enabled
    assert p.override_storage is None


def test_proj_uncoercible():
    with pytest.raises(ValidationError) as exc_info:
        Config(projects=["valid", UnCoercible()])

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Projects Format"
    assert error["type"] == "value_error"

    with pytest.raises(ValidationError) as exc_info:
        Config(projects=UnCoercible())

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Projects Format"
    assert error["type"] == "value_error"


#############
# ENVIRONMENT
#############

def test_env_empty():
    c = Config(environment=None)

    assert c.environment == {}


def test_env_dict():
    c = Config(environment={})

    assert c.environment == {}

    c = Config(environment={"variable": "value"})

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] == "value"


def test_env_list():
    c = Config(environment=[])

    assert c.environment == {}

    c = Config(environment=[
        "variable=value",
    ])

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] == "value"

    c = Config(environment=[
        "variable",
    ])

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] is None

    c = Config(environment=[
        123,
    ])

    assert len(c.environment) == 1
    assert "123" in c.environment
    assert c.environment["123"] is None


def test_env_coercible():
    c = Config(environment="variable=value")

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] == "value"

    c = Config(environment="variable")

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] is None

    c = Config(environment=123)

    assert len(c.environment) == 1
    assert "123" in c.environment
    assert c.environment["123"] is None

    c = Config(environment=123.4)

    assert len(c.environment) == 1
    assert "123.4" in c.environment
    assert c.environment["123.4"] is None


def test_env_uncoercible():
    with pytest.raises(ValidationError) as exc_info:
        Config(environment=UnCoercible())

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Environment Format"
    assert error["type"] == "value_error"

    with pytest.raises(ValidationError) as exc_info:
        Config(environment=["valid", UnCoercible()])

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Environment Format"
    assert error["type"] == "value_error"


#########
# STORAGE
#########

def test_storage_empty():
    with pytest.raises(ValidationError) as exc_info:
        Config(storage=None)

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "No Storage Given"
    assert error["type"] == "value_error"


def test_storage_dict():
    c = Config(storage={"directory": "/test/directory"})

    assert c.storage.directory == Path("/test/directory")


def test_storage_invalid_dict():
    with pytest.raises(ValidationError) as exc_info:
        Config(storage={"random key": "random value"})

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Storage Format"
    assert error["type"] == "value_error"


def test_storage_str():
    c = Config(storage="/test/directory")

    assert c.storage.directory == Path("/test/directory")


def test_storage_list():
    c = Config(storage=["/test/directory"])

    assert c.storage.directory == Path("/test/directory")


def test_storage_invalid():
    with pytest.raises(ValidationError) as exc_info:
        Config(storage=True)

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Storage Format"
    assert error["type"] == "value_error"


#########
# NETWORK
#########

def test_network_empty():
    with pytest.raises(ValidationError) as exc_info:
        Config(network=None)

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "No Network Given"
    assert error["type"] == "value_error"


def test_network_dict():
    c = Config(network={
        "name": "test_hub",
        "cidr": "1.2.3.4/32",
    })

    assert c == Config(network={
        "name": "TEST_HUB",
        "cidr": "1.2.3.4/32",
    })

    assert c.network.name == "test_hub"
    assert c.network.cidr == IPv4Network("1.2.3.4/32")


def test_network_invalid_dict():
    with pytest.raises(ValidationError) as exc_info:
        Config(network={"name": "test_hub"})

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "field required"
    assert error["type"] == "value_error.missing"

    with pytest.raises(ValidationError) as exc_info:
        Config(network={
            "name": "test_hub",
            "cidr": "1.2.3.4/123",
        })

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "value is not a valid IPv4 network"
    assert error["type"] == "value_error.ipv4network"


def test_network_invalid():
    with pytest.raises(ValidationError) as exc_info:
        Config(network=True)

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Network Format"
    assert error["type"] == "value_error"
