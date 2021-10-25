from pathlib import Path

import pytest

from kiwi_scp.instance import Project


def test_example():
    p = Project.from_directory(Path("example/hello-world.project"))

    assert p.directory == Path("example/hello-world.project")
    assert p.services != []


def test_caching():
    p = Project.from_directory(Path("example/hello-world.project"))

    assert p is Project.from_directory(Path("example/hello-world.project"))


def test_no_such_dir():
    nonexistent_path = Path("nonexistent")

    with pytest.raises(FileNotFoundError) as exc_info:
        Project.from_directory(nonexistent_path)

    from kiwi_scp._constants import COMPOSE_FILE_NAME
    assert exc_info.value.filename == str(nonexistent_path.joinpath(COMPOSE_FILE_NAME))
