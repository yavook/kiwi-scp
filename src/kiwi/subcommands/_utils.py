import os
import subprocess

from ..core import Parser
from ..config import LoadedConfig


def is_executable(filename):
    if filename is None:
        return False

    return os.path.isfile(filename) and os.access(filename, os.X_OK)


def find_exe_file(exe_name):
    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, exe_name)
        if is_executable(exe_file):
            return exe_file

    return None


def get_exe_key(exe_name):
    return f'executables:{exe_name}'


class SubCommand:
    __name = None
    __parser = None

    def __init__(self, name, **kwargs):
        self.__name = name
        self.__parser = Parser().get_subparsers().add_parser(name, **kwargs)

    def __str__(self):
        return self.__name

    def get_parser(self):
        return self.__parser

    def run(self):
        pass


class Docker:
    __requires_root = None

    @classmethod
    def __check_requires_root(cls):
        if cls.__requires_root is None:
            try:
                config = LoadedConfig.get()
                subprocess.run(
                    [config[get_exe_key('docker')], 'ps'],
                    check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                cls.__requires_root = False
            except subprocess.CalledProcessError:
                cls.__requires_root = True

        return cls.__requires_root

    @classmethod
    def run_command(cls, exe_key, args, cwd=None, env=None):
        config = LoadedConfig.get()
        cmd = [config[get_exe_key(exe_key)], *args]

        if cls.__check_requires_root():
            cmd = [config[get_exe_key('sudo')], *cmd]

        print(cmd)
        return subprocess.run(
            cmd,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            cwd=cwd, env=env
        )
