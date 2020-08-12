# system
import copy
import logging
import os
import re
import yaml

# local
from ._constants import KIWI_ROOT, KIWI_CONF_NAME

###########
# CONSTANTS

HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/kiwi_default.yml"
VERSION_TAG_NAME = f"{KIWI_ROOT}/version-tag"


class Config:
    __yml_content = {}

    def __key_resolve(self, key):
        # "a:b:c" => path = ['a', 'b'], key = 'c'
        path = key.split(':')
        path, key = path[:-1], path[-1]

        # resolve path
        container = self.__yml_content
        for step in path:
            container = container[step]

        return container, key

    def __getitem__(self, key):
        container, key = self.__key_resolve(key)
        return container[key]

    def __setitem__(self, key, value):
        container, key = self.__key_resolve(key)
        container[key] = value

    def __str__(self):
        # dump yml content
        yml_string = yaml.dump(self.__yml_content, default_flow_style=False, sort_keys=False)

        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # load header comment from file
        with open(HEADER_KIWI_CONF_NAME, 'r') as stream:
            yml_string = stream.read() + yml_string

        return yml_string

    def _update_from_file(self, filename):
        with open(filename, 'r') as stream:
            try:
                self.__yml_content.update(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                logging.error(exc)

    def clone(self):
        result = Config()
        result.__yml_content = copy.deepcopy(self.__yml_content)

        return result

    def save(self):
        with open(KIWI_CONF_NAME, 'w') as stream:
            stream.write(str(self))


class DefaultConfig(Config):
    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            cls.__instance = cls()
            cls.__instance._update_from_file(DEFAULT_KIWI_CONF_NAME)

            with open(VERSION_TAG_NAME, 'r') as stream:
                cls.__instance["version"] = stream.read().strip()

        return cls.__instance


class LoadedConfig(Config):
    @classmethod
    def get(cls):
        result = DefaultConfig.get().clone()

        if os.path.isfile(KIWI_CONF_NAME):
            result._update_from_file(KIWI_CONF_NAME)

        return result
