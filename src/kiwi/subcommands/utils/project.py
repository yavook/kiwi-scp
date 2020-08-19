import logging
import os

from ..._constants import CONF_DIRECTORY_NAME
from ...config import LoadedConfig


class Project:
    __name = None

    def __init__(self, name):
        self.__name = name

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
        return f"{self.enabled_dir_name()}{LoadedConfig.get()['markers:down']}"

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


def _extract_project_name(file_name):
    config = LoadedConfig.get()
    enabled_suffix = config['markers:project']
    disabled_suffix = f"{enabled_suffix}{config['markers:down']}"

    if os.path.isdir(file_name):
        # all subdirectories
        if file_name.endswith(enabled_suffix):
            # enabled projects
            return file_name[:-len(enabled_suffix)]

        elif file_name.endswith(disabled_suffix):
            # disabled projects
            return file_name[:-len(disabled_suffix)]

    return None


class Projects:
    __projects = None

    def __init__(self, names):
        self.__projects = [
            Project(name)
            for name in names if isinstance(name, str)
        ]

    def __getitem__(self, item):
        return self.__projects[item]

    @classmethod
    def all(cls):
        return cls([
            _extract_project_name(file_name)
            for file_name in os.listdir()
        ])

    @classmethod
    def from_args(cls, args):
        if args is not None and 'projects' in args:
            if isinstance(args.projects, list) and args.projects:
                return cls(args.projects)

            elif isinstance(args.projects, str):
                return cls([args.projects])

        return []
