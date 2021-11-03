from ruamel.yaml import CommentedMap

from kiwi_scp.instance import Service, Services


class TestServices:
    def test_empty(self):
        s = Service(
            name="s",
            content=CommentedMap(),
        )
        ss = Services([s])

        assert str(ss) == "services:\n  s: {}"
