# system
import copy
import logging
import os
import re
import yaml

# local
from ._constants import KIWI_CONF_NAME, HEADER_KIWI_CONF_NAME, DEFAULT_KIWI_CONF_NAME, VERSION_TAG_NAME


class Config:
    """represents a kiwi.yml"""

    __yml_content = {}
    __keys = {
        'version': "kiwi-scp version to use in this instance",

        'runtime:storage': "local directory for service data",
        'runtime:shells': "shell preference for working in service containers",
        'runtime:env': "common environment for compose yml",

        'markers:project': "marker string for project directories",
        'markers:disabled': "marker string for disabled projects",

        'network:name': "name for local network hub",
        'network:cidr': "CIDR block for local network hub",
    }

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
        yml_string = yaml.dump(
            self.__yml_content,
            default_flow_style=False, sort_keys=False
        ).strip()

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

    def user_query(self, key):
        """query user for new config value"""

        # prompt user as per argument
        try:
            result = input(f"Enter {self.__keys[key]} [{self[key]}] ").strip()
        except EOFError:
            print()
            result = None

        # store result if present
        if result:
            self[key] = result

    def save(self):
        """save current yml representation in current directory's kiwi.yml"""

        with open(KIWI_CONF_NAME, 'w') as stream:
            stream.write(str(self))
            stream.write('\n')


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
    def get(cls, directory='.'):
        if directory not in LoadedConfig.__instances:
            # create singleton for new path
            result = DefaultConfig.get()

            # update with that dir's kiwi.yml
            try:
                result = result._update_from_file(os.path.join(directory, KIWI_CONF_NAME))
            except FileNotFoundError:
                logging.info(f"No '{KIWI_CONF_NAME}' found at '{directory}'. Using defaults.")

            LoadedConfig.__instances[directory] = result

        # return singleton
        return LoadedConfig.__instances[directory]
