from pathlib import Path

from kiwi_scp.instance import Project


def test_example():
    p = Project.from_directory(Path("example/hello-world.project"))

    assert p.directory == Path("example/hello-world.project")
    assert len(p.services) == 5

    s = p.services[0]
    assert s.name == "greeter"
    assert len(s.configs) == 0

    s = p.services[1]
    assert s.name == "web"
    assert len(s.configs) == 0

    s = p.services[2]
    assert s.name == "db"
    assert len(s.configs) == 0

    s = p.services[3]
    assert s.name == "adminer"
    assert len(s.configs) == 0

    s = p.services[4]
    assert s.name == "another-web"
    assert len(s.configs) == 1
    assert s.configs[0] == Path("html/index.html")

