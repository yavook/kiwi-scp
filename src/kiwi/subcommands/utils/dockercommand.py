import subprocess

from .executable import Executable


class DockerCommand:
    __requires_root = None
    __exe = None

    def __init__(self, exe_name):
        if DockerCommand.__requires_root is None:
            try:
                Executable('docker').run(
                    ['ps'], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                DockerCommand.__requires_root = False
            except subprocess.CalledProcessError:
                DockerCommand.__requires_root = True

        self.__exe = Executable(exe_name, DockerCommand.__requires_root)

    def __getattr__(self, item):
        return getattr(self.__exe, item)

    def run_less(self, args, **kwargs):
        process = self.Popen(
            args, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            **kwargs
        )

        less_process = Executable('less').run(
            ['-R', '+G'], stdin=process.stdout
        )

        process.communicate()
        return less_process
