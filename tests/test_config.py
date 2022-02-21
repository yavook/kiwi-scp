from ipaddress import IPv4Network
from pathlib import Path

import pytest
from pydantic import ValidationError

from kiwi_scp.config import KiwiConfig
from kiwi_scp.yaml import YAML


class UnCoercible:
    """A class that doesn't have a string representation"""

    def __str__(self):
        raise ValueError


class TestDefault:
    def test(self):
        import toml

        c = KiwiConfig()
        version = toml.load("./pyproject.toml")["tool"]["poetry"]["version"]

        assert c == KiwiConfig.from_default()

        assert c.version == version
        assert len(c.shells) == 1
        assert c.shells[0] == Path("/bin/bash")
        assert c.projects == []
        assert c.environment == {}
        assert c.storage.directory == Path("/var/local/kiwi")
        assert c.network.name == "kiwi_hub"
        assert c.network.cidr == IPv4Network("10.22.46.0/24")

        kiwi_dict = {
            "version": version,
            "shells": ["/bin/bash"],
            "storage": {"directory": "/var/local/kiwi"},
            "network": {
                "name": "kiwi_hub",
                "cidr": "10.22.46.0/24",
            },
        }
        assert c.kiwi_dict == kiwi_dict

        assert c.kiwi_yml == YAML().dump_kiwi_yml(kiwi_dict)


class TestVersion:
    def test_valid(self):
        c = KiwiConfig(version="0.0.0")
        assert c.version == "0.0.0"

        c = KiwiConfig(version="0.0")
        assert c.version == "0.0"

        c = KiwiConfig(version="0")
        assert c.version == "0"

        c = KiwiConfig(version=1.0)
        assert c.version == "1.0"

        c = KiwiConfig(version=1)
        assert c.version == "1"

    def test_invalid(self):
        # definitely not a version
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(version="dnaf")

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"].find("string does not match regex") != -1
        assert error["type"] == "value_error.str.regex"

        # almost a version
        with pytest.raises(ValidationError) as exc_info:
            c = KiwiConfig(version="0.0.0alpha")
            print(c.version)

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"].find("string does not match regex") != -1
        assert error["type"] == "value_error.str.regex"


class TestShells:
    def test_empty(self):
        c = KiwiConfig(shells=None)

        assert c == KiwiConfig(shells=[])

        assert c.shells == []

    def test_list(self):
        c = KiwiConfig(shells=["/bin/sh", "sh"])

        assert len(c.shells) == 2
        assert c.shells[0] == Path("/bin/sh")
        assert c.shells[1] == Path("sh")

        c = KiwiConfig(shells=["/bin/bash"])

        assert len(c.shells) == 1
        assert c.shells[0] == Path("/bin/bash")

    def test_dict(self):
        c = KiwiConfig(shells={"/bin/bash": None})

        assert len(c.shells) == 1
        assert c.shells[0] == Path("/bin/bash")

    def test_coercible(self):
        c = KiwiConfig(shells="/bin/bash")

        assert c == KiwiConfig(shells=Path("/bin/bash"))

        assert len(c.shells) == 1
        assert c.shells[0] == Path("/bin/bash")

        c = KiwiConfig(shells=123)

        assert len(c.shells) == 1
        assert c.shells[0] == Path("123")

    def test_uncoercible(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(shells=UnCoercible())

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Shells Format"
        assert error["type"] == "value_error"

        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(shells=["/bin/bash", UnCoercible()])

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "value is not a valid path"
        assert error["type"] == "type_error.path"


class TestProject:
    def test_empty(self):
        c = KiwiConfig(projects=None)

        assert c == KiwiConfig(projects=[])
        assert c.projects == []

        assert c.get_project_config("invalid") is None

    def test_long(self):
        kiwi_dict = {
            "name": "project",
            "enabled": False,
            "override_storage": {"directory": "/test/directory"},
        }
        c = KiwiConfig(projects=[kiwi_dict])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert p == c.get_project_config("project")
        assert not p.enabled
        assert p.override_storage is not None

        assert c.kiwi_dict["projects"][0] == kiwi_dict

    def test_storage_str(self):
        kiwi_dict = {
            "name": "project",
            "enabled": False,
            "override_storage": "/test/directory",
        }
        c = KiwiConfig(projects=[kiwi_dict])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert not p.enabled
        assert p.override_storage is not None

    def test_storage_list(self):
        kiwi_dict = {
            "name": "project",
            "enabled": False,
            "override_storage": ["/test/directory"],
        }
        c = KiwiConfig(projects=[kiwi_dict])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert not p.enabled
        assert p.override_storage is not None

    def test_storage_invalid(self):
        kiwi_dict = {
            "name": "project",
            "enabled": False,
            "override_storage": True,
        }
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(projects=[kiwi_dict])

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Storage Format"
        assert error["type"] == "value_error"

    def test_short(self):
        kiwi_dict = {
            "project": False,
        }
        c = KiwiConfig(projects=[kiwi_dict])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert not p.enabled
        assert p.override_storage is None

        resulting_kiwi_dict = {
            "name": "project",
            "enabled": False,
        }
        assert p.kiwi_dict == resulting_kiwi_dict

    def test_dict(self):
        c = KiwiConfig(projects={"name": "project"})

        assert c == KiwiConfig(projects=[{"name": "project"}])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert p.enabled
        assert p.override_storage is None

    def test_invalid_dict(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(projects={
                "random key 1": "random value 1",
                "random key 2": "random value 2",
            })

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Project Format"
        assert error["type"] == "value_error"

    def test_coercible(self):
        c = KiwiConfig(projects="project")

        assert c == KiwiConfig(projects=["project"])

        assert len(c.projects) == 1
        p = c.projects[0]
        assert p.name == "project"
        assert p.enabled
        assert p.override_storage is None

    def test_uncoercible(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(projects=["valid", UnCoercible()])

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Projects Format"
        assert error["type"] == "value_error"

        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(projects=UnCoercible())

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Projects Format"
        assert error["type"] == "value_error"


class TestEnvironment:
    def test_empty(self):
        c = KiwiConfig(environment=None)

        assert c.environment == {}

    def test_dict(self):
        c = KiwiConfig(environment={})

        assert c.environment == {}

        kiwi_dict = {"variable": "value"}
        c = KiwiConfig(environment=kiwi_dict)

        assert len(c.environment) == 1
        assert "variable" in c.environment
        assert c.environment["variable"] == "value"

        assert c.kiwi_dict["environment"] == kiwi_dict

    def test_list(self):
        c = KiwiConfig(environment=[])

        assert c.environment == {}

        c = KiwiConfig(environment=[
            "variable=value",
        ])

        assert len(c.environment) == 1
        assert "variable" in c.environment
        assert c.environment["variable"] == "value"

        c = KiwiConfig(environment=[
            "variable",
        ])

        assert len(c.environment) == 1
        assert "variable" in c.environment
        assert c.environment["variable"] is None

        c = KiwiConfig(environment=[
            123,
        ])

        assert len(c.environment) == 1
        assert "123" in c.environment
        assert c.environment["123"] is None

    def test_coercible(self):
        c = KiwiConfig(environment="variable=value")

        assert len(c.environment) == 1
        assert "variable" in c.environment
        assert c.environment["variable"] == "value"

        c = KiwiConfig(environment="variable")

        assert len(c.environment) == 1
        assert "variable" in c.environment
        assert c.environment["variable"] is None

        c = KiwiConfig(environment=123)

        assert len(c.environment) == 1
        assert "123" in c.environment
        assert c.environment["123"] is None

        c = KiwiConfig(environment=123.4)

        assert len(c.environment) == 1
        assert "123.4" in c.environment
        assert c.environment["123.4"] is None

    def test_uncoercible(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(environment=UnCoercible())

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Environment Format"
        assert error["type"] == "value_error"

        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(environment=["valid", UnCoercible()])

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Environment Format"
        assert error["type"] == "value_error"


class TestStorage:
    def test_empty(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(storage=None)

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "No Storage Given"
        assert error["type"] == "value_error"

    def test_dict(self):
        kiwi_dict = {"directory": "/test/directory"}
        c = KiwiConfig(storage=kiwi_dict)

        assert c.storage.directory == Path("/test/directory")
        assert c.storage.kiwi_dict == kiwi_dict

    def test_invalid_dict(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(storage={"random key": "random value"})

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Storage Format"
        assert error["type"] == "value_error"

    def test_str(self):
        c = KiwiConfig(storage="/test/directory")

        assert c.storage.directory == Path("/test/directory")

    def test_list(self):
        c = KiwiConfig(storage=["/test/directory"])

        assert c.storage.directory == Path("/test/directory")

    def test_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(storage=True)

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Storage Format"
        assert error["type"] == "value_error"


class TestNetwork:
    def test_empty(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(network=None)

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "No Network Given"
        assert error["type"] == "value_error"

    def test_dict(self):
        kiwi_dict = {
            "name": "test_hub",
            "cidr": "1.2.3.4/32",
        }
        c = KiwiConfig(network=kiwi_dict)

        assert c == KiwiConfig(network={
            "name": "TEST_HUB",
            "cidr": "1.2.3.4/32",
        })

        assert c.network.name == "test_hub"
        assert c.network.cidr == IPv4Network("1.2.3.4/32")
        assert c.network.kiwi_dict == kiwi_dict

    def test_invalid_dict(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(network={"name": "test_hub"})

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "field required"
        assert error["type"] == "value_error.missing"

        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(network={
                "name": "test_hub",
                "cidr": "1.2.3.4/123",
            })

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "value is not a valid IPv4 network"
        assert error["type"] == "value_error.ipv4network"

    def test_invalid(self):
        with pytest.raises(ValidationError) as exc_info:
            KiwiConfig(network=True)

        assert len(exc_info.value.errors()) == 1
        error = exc_info.value.errors()[0]
        assert error["msg"] == "Invalid Network Format"
        assert error["type"] == "value_error"
