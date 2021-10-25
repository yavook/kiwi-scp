from pathlib import Path

from kiwi_scp.instance import Service


def test_no_description():
    s = Service.from_description(
        name="s",
        description={},
    )

    assert s.name == "s"
    assert s.configs == []


def test_no_configs():
    s = Service.from_description(
        name="s",
        description={
            "image": "repo/image:tag",
        },
    )

    assert s.name == "s"
    assert s.configs == []


def test_no_configs_in_volumes():
    s = Service.from_description(
        name="s",
        description={
            "image": "repo/image:tag",
            "volumes": [
                "docker_volume/third/dir:/path/to/third/mountpoint",
                "${TARGETDIR}/some/dir:/path/to/some/mountpoint",
                "$TARGETDIR/other/dir:/path/to/other/mountpoint",
            ]
        },
    )

    assert s.name == "s"
    assert s.configs == []


def test_with_configs():
    s = Service.from_description(
        name="s",
        description={
            "image": "repo/image:tag",
            "volumes": [
                "${CONFDIR}/some/config:/path/to/some/config",
                "$CONFDIR/other/config:/path/to/other/config",
            ]
        },
    )

    assert s.name == "s"
    assert len(s.configs) == 2
    assert s.configs == [
        Path("some/config"),
        Path("other/config"),
    ]
