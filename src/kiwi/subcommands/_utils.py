import logging
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


class DockerCommand:
    class __DockerCommand:
        __cmd = []

        def __init__(self, exe_name):
            config = LoadedConfig.get()
            self.__cmd = [config[get_exe_key(exe_name)]]

            if DockerCommand.__requires_root:
                self.__cmd = [config[get_exe_key("sudo")], *self.__cmd]

        def __build_cmd(self, args, **kwargs):
            cmd = [*self.__cmd, *args]
            logging.debug(f"DockerProgram cmd{cmd}, kwargs{kwargs}")
            return cmd

        def run(self, args, **kwargs):
            return subprocess.run(
                self.__build_cmd(args, **kwargs),
                **kwargs
            )

        def run_less(self, args, **kwargs):
            process = subprocess.Popen(
                self.__build_cmd(args, **kwargs),
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                **kwargs
            )

            less_process = subprocess.run(
                ['less', '-R', '+G'],
                stdin=process.stdout
            )

            process.communicate()
            return less_process

    __exe_name = None
    __instances = {}
    __requires_root = None

    def __init__(self, exe_name):
        if DockerCommand.__requires_root is None:
            try:
                config = LoadedConfig.get()
                subprocess.run(
                    [config[get_exe_key('docker')], 'ps'],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                DockerCommand.__requires_root = False
            except subprocess.CalledProcessError:
                DockerCommand.__requires_root = True

        self.__exe_name = exe_name

        if exe_name not in DockerCommand.__instances:
            DockerCommand.__instances[exe_name] = DockerCommand.__DockerCommand(exe_name)

    def __getattr__(self, item):
        return getattr(self.__instances[self.__exe_name], item)
