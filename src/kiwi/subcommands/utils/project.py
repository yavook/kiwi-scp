import logging
import os

from kiwi._constants import CONF_DIRECTORY_NAME
from kiwi.config import LoadedConfig


class Project:
    __name = None
    __config = None

    def __init__(self, name):
        self.__name = name
        self.__config = LoadedConfig.get()

    @classmethod
    def from_names(cls, names):
        return [cls(name) for name in names]

    @classmethod
    def all(cls):
        # current directory content
        content = os.listdir()

        # filter subdirectories
        dirs = [dir_name for dir_name in content if os.path.isdir(dir_name)]

        # filter by suffix
        project_dirs = [dir_name for dir_name in dirs if dir_name.endswith(cls.__config['markers:project'])]

        # remove suffix
        project_names = [project_name[:-len(cls.__config['markers:project'])] for project_name in project_dirs]

        return cls.from_names(project_names)

    @classmethod
    def from_args(cls, args):
        if args is not None and 'projects' in args:
            if isinstance(args.projects, list) and args.projects:
                return cls.from_names(args.projects)
            elif isinstance(args.projects, str):
                return cls.from_names([args.projects])

        return []

    def get_name(self):
        return self.__name

    def dir_name(self):
        return f"{self.__name}{self.__config['markers:project']}"

    def down_dir_name(self):
        return f"{self.dir_name()}{self.__config['markers:down']}"

    def conf_dir_name(self):
        return os.path.join(self.dir_name(), CONF_DIRECTORY_NAME)

    def target_dir_name(self):
        return os.path.join(self.__config['runtime:storage'], self.dir_name())

    def exists(self):
        return os.path.isdir(self.dir_name()) or os.path.isdir(self.down_dir_name())

    def is_enabled(self):
        return os.path.isdir(self.dir_name())

    def is_disabled(self):
        return os.path.isdir(self.down_dir_name())

    def has_configs(self):
        return os.path.isdir(self.dir_name())

    def enable(self):
        if self.is_disabled():
            logging.info(f"Enabling project '{self.get_name()}'")
            os.rename(self.down_dir_name(), self.dir_name())

        elif self.is_enabled():
            logging.warning(f"Project '{self.get_name()}' is enabled!")

        else:
            logging.warning(f"Project '{self.get_name()}' not found in instance!")
            return False

        return True

    def disable(self):
        if self.is_enabled():
            logging.info(f"Disabling project '{self.get_name()}'")
            os.rename(self.dir_name(), self.down_dir_name())

        elif self.is_disabled():
            logging.warning(f"Project '{self.get_name()}' is disabled!")

        else:
            logging.warning(f"Project '{self.get_name()}' not found in instance!")
            return False

        return True