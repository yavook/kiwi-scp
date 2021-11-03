from pathlib import Path

from kiwi_scp.instance import Instance


class TestDefault:
    def test_example(self):
        i = Instance(Path("example"))

        assert i.config is not None
        assert len(i.config.projects) == 1

        pc = i.config.projects[0]

        assert pc.name == "hello-world.project"

        p = i.get_project("hello-world.project")

        assert p.directory == Path("example/hello-world.project")

        assert i.get_project("nonexistent") is None

    def test_empty(self):
        i = Instance()

        assert i.config is not None
        assert len(i.config.projects) == 0

    def test_no_such_dir(self):
        nonexistent_path = Path("nonexistent")
        i = Instance(nonexistent_path)

        assert i.directory == nonexistent_path
        assert i.config is not None
        assert len(i.config.projects) == 0
