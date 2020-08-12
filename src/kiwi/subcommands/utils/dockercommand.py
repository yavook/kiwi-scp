import subprocess

from .executable import Executable


class DockerCommand(Executable):
    __requires_root = None

    def __init__(self, exe_name):
        super().__init__(exe_name)

        if DockerCommand.__requires_root is None:
            try:
                Executable('docker').run(
                    ['ps'],
                    check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                DockerCommand.__requires_root = False
            except subprocess.CalledProcessError:
                DockerCommand.__requires_root = True

    def run(self, args, **kwargs):
        # equivalent to 'super().run' but agnostic of nested class construct
        super().__getattr__("run")(
            args, DockerCommand.__requires_root,
            **kwargs
        )

    def run_less(self, args, **kwargs):
        process = self.Popen(
            args, DockerCommand.__requires_root,
            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            **kwargs
        )

        less_process = Executable('less').run(
            ['-R', '+G'],
            stdin=process.stdout
        )

        process.communicate()
        return less_process
