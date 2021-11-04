import functools
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, List, Any

import attr

_logger = logging.getLogger(__name__)


@attr.s
class Executable:
    exe_name: str = attr.ib()

    @staticmethod
    @functools.lru_cache(maxsize=None)
    def __find_exe_file(exe_name: str) -> Optional[Path]:
        for path in os.environ['PATH'].split(os.pathsep):
            exe_file = Path(path).joinpath(exe_name)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                return exe_file

        raise FileNotFoundError(f"Executable '{exe_name}' not found in $PATH!")

    @property
    def exe_file(self) -> Optional[Path]:
        return self.__find_exe_file(self.exe_name)

    def __build_cmd(self, args, kwargs) -> List:
        cmd = [self.exe_file, *args]

        _logger.debug(f"Executable cmd{cmd}, kwargs{kwargs}")
        return cmd

    def run(self, process_args, **kwargs) -> Optional[subprocess.CompletedProcess]:
        return subprocess.run(
            self.__build_cmd(process_args, kwargs),
            **kwargs
        )

    def Popen(self, process_args, **kwargs) -> subprocess.Popen:
        return subprocess.Popen(
            self.__build_cmd(process_args, kwargs),
            **kwargs
        )

    def run_less(self, process_args, **kwargs) -> Optional[subprocess.CompletedProcess]:
        kwargs['stdout'] = subprocess.PIPE
        kwargs['stderr'] = subprocess.DEVNULL

        with self.Popen(process_args, **kwargs) as process:
            less_process = Executable('less').run([
                '-R', '+G'
            ], stdin=process.stdout)

            process.communicate()

        return less_process
