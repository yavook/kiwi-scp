from pathlib import Path

import pytest

from kiwi_scp._constants import COMPOSE_FILE_NAME
from kiwi_scp.instance import Project


class TestDefault:
    def test_example(self):
        p = Project(Path("example/hello-world.project"))

        ss = p.get_services()

        assert len(ss.content) == 5

        s = ss.content[0]

        assert s.name == "greeter"

        ss2 = p.get_services(["nonexistent"])

        assert len(ss2.content) == 0

    def test_empty(self):
        p = Project(Path("nonexistent"))

        with pytest.raises(FileNotFoundError) as exc_info:
            p.get_services()

        assert exc_info.value.filename == f"nonexistent/{COMPOSE_FILE_NAME}"
