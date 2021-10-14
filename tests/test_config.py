from ipaddress import IPv4Network
from pathlib import Path

import pytest
import toml
from pydantic import ValidationError

from kiwi_scp.config import Config


def test_default():
    c = Config()
    version = toml.load("./pyproject.toml")["tool"]["poetry"]["version"]

    assert c.version == version
    assert len(c.shells) == 1
    assert c.shells[0] == Path("/bin/bash")
    assert c.projects is None
    assert c.environment == {}
    assert c.storage.directory == Path("/var/local/kiwi")
    assert c.network.name == "kiwi_hub"
    assert c.network.cidr == IPv4Network("10.22.46.0/24")


#############
# ENVIRONMENT
#############

def test_env_empty():
    c = Config(environment=None)

    assert c.environment == {}


def test_env_dict():
    c = Config(environment={})

    assert c.environment == {}

    c = Config(environment={
        "variable": "value"
    })

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


def test_env_str():
    c = Config(environment="variable=value")

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] == "value"

    c = Config(environment="variable")

    assert len(c.environment) == 1
    assert "variable" in c.environment
    assert c.environment["variable"] is None


def test_env_coercible():
    c = Config(environment=123)

    assert len(c.environment) == 1
    assert "123" in c.environment
    assert c.environment["123"] is None

    c = Config(environment=123.4)

    assert len(c.environment) == 1
    assert "123.4" in c.environment
    assert c.environment["123.4"] is None


def test_env_undef():
    class UnCoercible:
        def __str__(self):
            raise ValueError

    with pytest.raises(ValidationError) as exc_info:
        Config(environment=UnCoercible())

    assert len(exc_info.value.errors()) == 1
    error = exc_info.value.errors()[0]
    assert error["msg"] == "Invalid Environment Format"
    assert error["type"] == "value_error"
