from ruamel.yaml import CommentedMap

from kiwi_scp.services import Services
from kiwi_scp.service import Service


class TestServices:
    def test_empty(self):
        s = Service(
            name="s",
            content=CommentedMap(),
            parent_project=None,
        )
        ss = Services([s])

        assert str(ss) == "services:\n  s: {}\nconfigs: []"
