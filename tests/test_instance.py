from pathlib import Path

from kiwi_scp.instance import Instance


def test_example():
    i = Instance(Path("example"))

    assert i.config is not None
    assert len(i.config.projects) == 1

    p = i.config.projects[0]

    assert p.name == "hello-world.project"


def test_empty():
    i = Instance()

    assert i.config is not None
    assert len(i.config.projects) == 0


def test_no_such_dir():
    nonexistent_path = Path("nonexistent")
    i = Instance(nonexistent_path)

    assert i.directory == nonexistent_path
    assert i.config is not None
    assert len(i.config.projects) == 0
