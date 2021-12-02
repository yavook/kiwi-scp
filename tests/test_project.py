from pathlib import Path

import pytest

from kiwi_scp._constants import COMPOSE_FILE_NAME
from kiwi_scp.config import KiwiConfig
from kiwi_scp.project import Project


class TestDefault:
    cfg = KiwiConfig()

    def test_example(self):
        p = Project(
            directory=Path("example/hello-world.project"),
            parent=None,
        )

        ss = p.services

        assert len(ss.content) == 5

        s = ss.content[0]

        assert s.name == "greeter"

        ss2 = p.services.filter_existing(["nonexistent"])

        assert len(ss2.content) == 0

    def test_empty(self):
        p = Project(
            directory=Path("nonexistent"),
            parent=None,
        )

        with pytest.raises(FileNotFoundError) as exc_info:
            _ = p.services

        assert exc_info.value.filename == f"nonexistent/{COMPOSE_FILE_NAME}"
