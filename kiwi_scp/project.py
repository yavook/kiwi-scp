import logging
import os

from ._constants import CONF_DIRECTORY_NAME
from .config import LoadedConfig
from .executable import Executable


class Project:
    __name = None

    def __init__(self, name):
        self.__name = name

    @classmethod
    def from_file_name(cls, file_name):
        if os.path.isdir(file_name):
            config = LoadedConfig.get()

            if file_name.endswith(config['markers:disabled']):
                file_name = file_name[:-len(config['markers:disabled'])]

            if file_name.endswith(config['markers:project']):
                file_name = file_name[:-len(config['markers:project'])]
                return cls(file_name)

        return None

    def get_name(self):
        return self.__name

    def dir_name(self):
        if self.is_enabled():
            return self.enabled_dir_name()
        elif self.is_disabled():
            return self.disabled_dir_name()
        else:
            return None

    def enabled_dir_name(self):
        return f"{self.__name}{LoadedConfig.get()['markers:project']}"

    def disabled_dir_name(self):
        return f"{self.enabled_dir_name()}{LoadedConfig.get()['markers:disabled']}"

    def conf_dir_name(self):
        return os.path.join(self.dir_name(), CONF_DIRECTORY_NAME)

    def compose_file_name(self):
        return os.path.join(self.dir_name(), 'docker-compose.yml')

    def target_dir_name(self):
        return os.path.join(LoadedConfig.get()['runtime:storage'], self.enabled_dir_name())

    def exists(self):
        return os.path.isdir(self.enabled_dir_name()) or os.path.isdir(self.disabled_dir_name())

    def is_enabled(self):
        return os.path.isdir(self.enabled_dir_name())

    def is_disabled(self):
        return os.path.isdir(self.disabled_dir_name())

    def has_configs(self):
        return os.path.isdir(self.conf_dir_name())

    def __update_kwargs(self, kwargs):
        if not self.is_enabled():
            # cannot compose in a disabled project
            logging.warning(f"Project '{self.get_name()}' is not enabled!")
            return False

        config = LoadedConfig.get()

        # execute command in project directory
        kwargs['cwd'] = self.dir_name()

        # ensure there is an environment
        if 'env' not in kwargs:
            kwargs['env'] = {}

        # create environment variables for docker commands
        kwargs['env'].update({
            'COMPOSE_PROJECT_NAME': self.get_name(),
            'KIWI_HUB_NAME': config['network:name'],
            'TARGETROOT': config['runtime:storage'],
            'CONFDIR': os.path.join(config['runtime:storage'], CONF_DIRECTORY_NAME),
            'TARGETDIR': self.target_dir_name()
        })

        # add common environment from config
        if config['runtime:env'] is not None:
            kwargs['env'].update(config['runtime:env'])

        logging.debug(f"kwargs updated: {kwargs}")

        return True

    def compose_run(self, compose_args, **kwargs):
        if self.__update_kwargs(kwargs):
            Executable('docker-compose').run(compose_args, **kwargs)

    def compose_run_less(self, compose_args, **kwargs):
        if self.__update_kwargs(kwargs):
            Executable('docker-compose').run_less(compose_args, **kwargs)

    def enable(self):
        if self.is_disabled():
            logging.info(f"Enabling project '{self.get_name()}'")
            os.rename(self.dir_name(), self.enabled_dir_name())

        elif self.is_enabled():
            logging.warning(f"Project '{self.get_name()}' is enabled!")

        else:
            logging.warning(f"Project '{self.get_name()}' not found in instance!")
            return False

        return True

    def disable(self):
        if self.is_enabled():
            logging.info(f"Disabling project '{self.get_name()}'")
            os.rename(self.dir_name(), self.disabled_dir_name())

        elif self.is_disabled():
            logging.warning(f"Project '{self.get_name()}' is disabled!")

        else:
            logging.warning(f"Project '{self.get_name()}' not found in instance!")
            return False

        return True
