from ruamel.yaml import CommentedMap

from kiwi_scp.services import Services
from kiwi_scp.service import Service


class TestServices:
    def test_empty(self):
        s = Service(
            name="s",
            content=CommentedMap(),
            parent=None,
        )
        ss = Services([s])

        assert str(ss) == "services:\n  s: {}"
