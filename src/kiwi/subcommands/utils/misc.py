import os


def get_project_names(args):
    """get project names from CLI args"""

    if args is not None and 'projects' in args:
        if isinstance(args.projects, list):
            if args.projects:
                return args.projects
            else:
                return None
        elif isinstance(args.projects, str):
            return [args.projects]

    return None


def get_first_project_name(args):
    """get first project name from CLI args"""

    names = get_project_names(args)
    if names is not None:
        return names[0]

    return None


def get_services(args):
    """get services list from CLI args"""

    if args is not None and 'services' in args:
        return args.services

    return None


def get_project_dir(config, project_name):
    """get project directory"""

    return f"{project_name}{config['markers:project']}"


def get_project_down_dir(config, project_name):
    """get project directory"""

    return f"{get_project_dir(config, project_name)}{config['markers:down']}"


def get_target_dir(config, project_name):
    """get project's target directory"""

    return os.path.join(config['runtime:storage'], get_project_dir(config, project_name))


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


def _surround(string, bang):
    midlane = f"{bang * 3} {string} {bang * 3}"
    sidelane = bang*len(midlane)

    return f"{sidelane}\n{midlane}\n{sidelane}"


def _emphasize(lines):
    if isinstance(lines, list):
        return '\n'.join([_emphasize(line) for line in lines])
    elif lines:
        return f">>> {lines} <<<"
    else:
        return lines

def are_you_sure(prompt, default="no"):
    if default.lower() == 'yes':
        suffix = "[YES|no]"
    else:
        suffix = "[yes|NO]"

    answer = input(
        f"{_surround('MUST HAVE CAREFULING IN PROGRESS', '!')}\n"
        f"\n"
        f"{_emphasize(prompt)}\n"
        f"\n"
        f"Are you sure you want to proceed? {suffix} "
    ).strip().lower()

    if answer == '':
        answer = default

    while answer not in ['yes', 'no']:
        answer = input("Please type 'yes' or 'no' explicitly: ").strip().lower()

    return answer == 'yes'
