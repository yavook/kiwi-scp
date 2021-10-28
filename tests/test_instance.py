from pathlib import Path

from kiwi_scp.instance import Instance


class TestDefault:
    def test_example(self):
        i = Instance(Path("example"))

        assert i.config is not None
        assert len(i.config.projects) == 1

        p = i.config.projects[0]

        assert p.name == "hello-world.project"

        ss = i.get_services(p.name)

        assert len(ss.content) == 5

        s = ss.content[0]

        assert s.name == "greeter"

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
