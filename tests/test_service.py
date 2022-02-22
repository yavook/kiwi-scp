from pathlib import Path

from ruamel.yaml import CommentedMap

from kiwi_scp.service import Service


class TestDefault:
    def test_empty(self):
        s = Service(
            name="s",
            content=CommentedMap(),
            parent_project=None,
        )

        assert s.name == "s"
        assert list(s.configs) == []

    def test_no_configs(self):
        s = Service(
            name="s",
            content=CommentedMap({
                "image": "repo/image:tag",
            }),
            parent_project=None,
        )

        assert s.name == "s"
        assert list(s.configs) == []

    def test_no_configs_in_volumes(self):
        s = Service(
            name="s",
            content=CommentedMap({
                "image": "repo/image:tag",
                "volumes": [
                    "docker_volume/third/dir:/path/to/third/mountpoint",
                    "${KIWI_PROJECT}/some/dir:/path/to/some/mountpoint",
                    "$KIWI_PROJECT/other/dir:/path/to/other/mountpoint",
                ]
            }),
            parent_project=None,
        )

        assert s.name == "s"
        assert list(s.configs) == []

    def test_with_configs(self):
        s = Service(
            name="s",
            content=CommentedMap({
                "image": "repo/image:tag",
                "volumes": [
                    "${KIWI_CONFIG}/some/config:/path/to/some/config",
                    "$KIWI_CONFIG/other/config:/path/to/other/config",
                ]
            }),
            parent_project=None,
        )

        assert s.name == "s"
        assert len(list(s.configs)) == 2
        assert list(s.configs) == [
            Path("some/config"),
            Path("other/config"),
        ]
