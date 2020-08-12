import os
import logging
import subprocess


def is_executable(filename):
    if filename is None:
        return False

    return os.path.isfile(filename) and os.access(filename, os.X_OK)


def find_exe_file(exe_name):
    for path in os.environ['PATH'].split(os.pathsep):
        exe_file = os.path.join(path, exe_name)
        if is_executable(exe_file):
            return exe_file

    raise FileNotFoundError(f"Executable '{exe_name}' not found in $PATH!")


class Executable:
    __exe_name = None
    __instances = {}

    class __Executable:
        __cmd = None

        def __init__(self, exe_name, requires_root=False):
            self.__cmd = [find_exe_file(exe_name)]

            if requires_root:
                self.__cmd = [find_exe_file("sudo"), *self.__cmd]

        def __build_cmd(self, args, **kwargs):
            cmd = [*self.__cmd, *args]
            logging.debug(f"Executable cmd{cmd}, kwargs{kwargs}")
            return cmd

        def run(self, args, **kwargs):
            return subprocess.run(
                self.__build_cmd(args, **kwargs),
                **kwargs
            )

        def Popen(self, args, **kwargs):
            return subprocess.Popen(
                self.__build_cmd(args, **kwargs),
                **kwargs
            )

    def __init__(self, exe_name, requires_root=False):
        self.__exe_name = exe_name

        if exe_name not in Executable.__instances:
            Executable.__instances[exe_name] = Executable.__Executable(exe_name, requires_root)

    def __getattr__(self, item):
        return getattr(self.__instances[self.__exe_name], item)
