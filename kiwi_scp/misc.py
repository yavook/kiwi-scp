import re
from typing import Any, Type, List, Callable, Optional

import attr
import click
import ruamel.yaml
import ruamel.yaml.compat
from click.decorators import FC

from ._constants import HEADER_KIWI_CONF_NAME


@attr.s
class _MultiDecorator:
    options: List[Callable[[FC], FC]] = attr.ib(factory=list)

    def __call__(self, target: FC):
        for option in reversed(self.options):
            target = option(target)

        return target


_project_arg = click.argument(
    "project",
    required=False,
    type=str,
)

_service_arg = click.argument(
    "service",
    required=False,
    type=str,
)

instance_command = _MultiDecorator([])
project_command = _MultiDecorator([_project_arg])
service_command = _MultiDecorator([_project_arg, _service_arg])


def user_query(description: str, default: Any, cast_to: Type[Any] = str):
    # prompt user as per argument
    while True:
        try:
            str_value = input(f"Enter {description} [{default}] ").strip()
            if str_value:
                return cast_to(str_value)
            else:
                return default

        except EOFError:
            click.echo("Input aborted.")
            return default

        except Exception as e:
            click.echo(f"Invalid input: {e}")


class YAML(ruamel.yaml.YAML):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent(offset=2)

    def dump(self, data, stream=None, **kwargs) -> Optional[str]:
        into_str: bool = False
        if stream is None:
            into_str = True
            stream = ruamel.yaml.compat.StringIO()

        super().dump(data, stream=stream, **kwargs)
        if into_str:
            return stream.getvalue()

    @staticmethod
    def _format_kiwi_yml(yml_string: str):
        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # load header comment from file
        with open(HEADER_KIWI_CONF_NAME, 'r') as stream:
            yml_string = stream.read() + yml_string

        return yml_string

    def dump_kiwi_yml(self, data, **kwargs) -> Optional[str]:
        return self.dump(data, transform=YAML._format_kiwi_yml, **kwargs)


def _surround(string, bang):
    midlane = f"{bang * 3} {string} {bang * 3}"
    sidelane = bang * len(midlane)

    return f"{sidelane}\n{midlane}\n{sidelane}"


def _emphasize(lines):
    if isinstance(lines, list):
        return '\n'.join([_emphasize(line) for line in lines])
    elif lines:
        return f">>> {lines} <<<"
    else:
        return lines


def are_you_sure(prompt, default="no"):
    if default.lower() == 'yes':
        suffix = "[YES|no]"
    else:
        suffix = "[yes|NO]"

    answer = input(
        f"{_surround('MUST HAVE CAREFULING IN PROCESS', '!')}\n"
        f"\n"
        f"{_emphasize(prompt)}\n"
        f"\n"
        f"Are you sure you want to proceed? {suffix} "
    ).strip().lower()

    if answer == '':
        answer = default

    while answer not in ['yes', 'no']:
        answer = input("Please type 'yes' or 'no' explicitly: ").strip().lower()

    return answer == 'yes'
