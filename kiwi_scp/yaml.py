import re
from typing import Optional

import ruamel.yaml
import ruamel.yaml.compat

from ._constants import HEADER_KIWI_CONF_NAME


class YAML(ruamel.yaml.YAML):
    def __init__(self, *args, **kwargs) -> None:
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
    def _format_kiwi_yml(yml_string: str) -> str:
        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # load header comment from file
        with open(HEADER_KIWI_CONF_NAME, 'r') as stream:
            yml_string = stream.read() + yml_string

        return yml_string

    def dump_kiwi_yml(self, data, **kwargs) -> Optional[str]:
        return self.dump(data, transform=YAML._format_kiwi_yml, **kwargs)
