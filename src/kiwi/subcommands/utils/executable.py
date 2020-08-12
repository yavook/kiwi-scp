import os


def get_exe_key(exe_name):
    return f'executables:{exe_name}'


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