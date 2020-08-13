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

# text files inside kiwi-config "src" directory
HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/kiwi_default.yml"
VERSION_TAG_NAME = f"{KIWI_ROOT}/version-tag"


class Config:
    """represents a kiwi.yml"""

    __yml_content = {}

    def __key_resolve(self, key):
        """
        Resolve nested dictionaries

        If __yml_content is {'a': {'b': {'c': "val"}}} and key is 'a:b:c',
        this returns a single dict {'c': "val"} and the direct key 'c'
        """

        # "a:b:c" => path = ['a', 'b'], key = 'c'
        path = key.split(':')
        path, key = path[:-1], path[-1]

        # resolve path
        container = self.__yml_content
        for step in path:
            container = container[step]

        return container, key

    def __getitem__(self, key):
        """array-like read access to __yml_content"""

        container, key = self.__key_resolve(key)
        return container[key]

    def __setitem__(self, key, value):
        """array-like write access to __yml_content"""

        container, key = self.__key_resolve(key)
        container[key] = value

    def __str__(self):
        """dump into textual representation"""

        # dump yml content
        yml_string = yaml.dump(self.__yml_content, default_flow_style=False, sort_keys=False)

        # insert newline before every main key
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        # load header comment from file
        with open(HEADER_KIWI_CONF_NAME, 'r') as stream:
            yml_string = stream.read() + yml_string

        return yml_string

    def _update_from_file(self, filename):
        """return a copy updated using a kiwi.yml file"""

        with open(filename, 'r') as stream:
            try:
                # create copy
                result = Config()
                result.__yml_content = copy.deepcopy(self.__yml_content)

                # read file
                logging.debug(f"Reading '{filename}' into '{id(result.__yml_content)}'")
                result.__yml_content.update(yaml.safe_load(stream))

                return result
            except yaml.YAMLError as exc:
                logging.error(exc)

    def save(self):
        """save current yml representation in current directory's kiwi.yml"""

        with open(KIWI_CONF_NAME, 'w') as stream:
            stream.write(str(self))


class DefaultConfig(Config):
    """Singleton: The default kiwi.yml file"""

    __instance = None

    @classmethod
    def get(cls):
        if cls.__instance is None:
            # create singleton
            cls.__instance = cls()._update_from_file(DEFAULT_KIWI_CONF_NAME)

            # add version data from separate file (keeps default config cleaner)
            with open(VERSION_TAG_NAME, 'r') as stream:
                cls.__instance['version'] = stream.read().strip()

        # return singleton
        return cls.__instance


class LoadedConfig(Config):
    """Singleton collection: kiwi.yml files by path"""

    __instances = {}

    @classmethod
    def get(cls):
        cwd = os.getcwd()

        if cwd not in LoadedConfig.__instances:
            # create singleton for new path
            result = DefaultConfig.get()

            # update with current dir's kiwi.yml
            try:
                result = result._update_from_file(KIWI_CONF_NAME)
            except FileNotFoundError:
                logging.info(f"No '{KIWI_CONF_NAME}' found at '{cwd}'. Using defaults.")

            LoadedConfig.__instances[cwd] = result

        # return singleton
        return LoadedConfig.__instances[cwd]
