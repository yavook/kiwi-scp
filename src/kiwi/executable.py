# system
import logging
import os
import subprocess

# local
from .config import LoadedConfig


def _is_executable(filename):
    if filename is None:
        return False

    return os.path.isfile(filename) and os.access(filename, os.X_OK)


def _find_exe_file(exe_name):
    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, exe_name)
        if _is_executable(exe_file):
            return exe_file

    raise FileNotFoundError(f"Executable '{exe_name}' not found in $PATH!")


class Executable:
    class __Executable:
        __exe_path = None

        def __init__(self, exe_name):
            self.__exe_path = _find_exe_file(exe_name)

        def __build_cmd(self, args, kwargs):
            cmd = [self.__exe_path, *args]

            logging.debug(f"Executable cmd{cmd}, kwargs{kwargs}")
            return cmd

        def run(self, process_args, **kwargs):
            return subprocess.run(
                self.__build_cmd(process_args, kwargs),
                **kwargs
            )

        def Popen(self, process_args, **kwargs):
            return subprocess.Popen(
                self.__build_cmd(process_args, kwargs),
                **kwargs
            )

        def run_less(self, process_args, **kwargs):
            kwargs['stdout'] = subprocess.PIPE
            kwargs['stderr'] = subprocess.DEVNULL

            process = self.Popen(
                process_args,
                **kwargs
            )

            less_process = Executable('less').run([
                '-R', '+G'
            ], stdin=process.stdout)

            process.communicate()
            return less_process

    __exe_name = None
    __instances = {}

    def __init__(self, exe_name):
        self.__exe_name = exe_name

        if exe_name not in Executable.__instances:
            Executable.__instances[exe_name] = Executable.__Executable(exe_name)

    def __getattr__(self, item):
        return getattr(self.__instances[self.__exe_name], item)
