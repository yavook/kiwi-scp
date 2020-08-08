import subprocess

from ..config import LoadedConfig


class SubCommand:
    @classmethod
    def get_cmd(cls):
        pass

    @classmethod
    def setup(cls):
        pass

    @classmethod
    def run(cls):
        pass


class Docker:
    __requires_root = None

    @classmethod
    def __check_requires_root(cls):
        if cls.__requires_root is None:
            try:
                config = LoadedConfig.get()
                subprocess.run(
                    [config['executables:docker'], 'ps'],
                    check=True,
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
                cls.__requires_root = False
            except subprocess.CalledProcessError:
                cls.__requires_root = True

        return cls.__requires_root

    @classmethod
    def run_command(cls, program, args, cwd=None, env=None):
        config = LoadedConfig.get()
        cmd = [config['executables:' + program], *args]

        if cls.__check_requires_root():
            cmd = [config['executables:sudo'], *cmd]

        print(cmd)
        return subprocess.run(
            cmd,
            # stdout=subprocess.PIPE,
            # stderr=subprocess.PIPE,
            cwd=cwd, env=env
        )
