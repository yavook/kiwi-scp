import logging
import re
import yaml

from .core import KIWI_ROOT, KIWI_CONF_NAME

###########
# CONSTANTS

DEFAULT_KIWI_CONF_NAME = KIWI_ROOT + "/default.kiwi.yml"


class Config:
    __yml_content = {}

    def __str__(self):
        # dump yml content
        yml_string = yaml.dump(self.__yml_content, default_flow_style=False, sort_keys=False)

        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # extract header comment from default config
        with open(DEFAULT_KIWI_CONF_NAME, 'r') as stream:
            yml_header = stream.read().strip()
            yml_header = re.sub(r'^[^#].*', r'', yml_header, flags=re.MULTILINE).strip()
            yml_string = "{}\n{}".format(yml_header, yml_string)

        return yml_string

    def __key_resolve(self, key):
        # "a:b:c" => path = ['a', 'b'], key = 'c'
        path = key.split(':')
        path, key = path[:-1], path[-1]

        # resolve path
        container = self.__yml_content
        for step in path:
            container = container[step]

        return container, key

    def __setitem__(self, key, value):
        container, key = self.__key_resolve(key)
        container[key] = value

    def __getitem__(self, key):
        container, key = self.__key_resolve(key)
        return container[key]

    def __update_from_file(self, filename):
        with open(filename, 'r') as stream:
            try:
                self.__yml_content.update(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                logging.error(exc)

    @classmethod
    def default(cls):
        result = cls()
        result.__update_from_file(DEFAULT_KIWI_CONF_NAME)

        with open(KIWI_ROOT + "/version-tag", 'r') as stream:
            result.__yml_content["version"] = stream.read().strip()

        return result

    @classmethod
    def load(cls):
        result = cls.default()
        result.__update_from_file(KIWI_CONF_NAME)

        return result

    def save(self):
        pass
