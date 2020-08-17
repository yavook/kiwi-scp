import os


def get_project_name(args):
    """get project name from CLI args"""

    if args is not None and 'projects' in args:
        if isinstance(args.projects, list) and len(args.projects) > 0:
            return args.projects[0]
        else:
            return args.projects

    return None


def get_project_dir(config, project_name):
    """get project directory"""

    return f"{project_name}{config['markers:project']}"


def get_target_dir(config, project_name):
    """get project's target directory"""

    return f"{config['runtime:storage']}{get_project_dir(config, project_name)}"


def list_projects(config):
    """list projects in current instance"""

    # complete dir listing
    content = os.listdir()

    # filter directories
    dirs = [d for d in content if os.path.isdir(d)]

    # filter suffix
    project_dirs = [p for p in dirs if p.endswith(config['markers:project'])]

    # remove suffix
    projects = [p[:-len(config['markers:project'])] for p in project_dirs]

    return projects
