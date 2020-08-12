import logging
import subprocess

from ...config import LoadedConfig
from .executable import get_exe_key


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