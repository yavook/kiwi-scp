import os

from kiwi.project import Project


class Projects:
    __projects = None

    def __getitem__(self, item):
        return self.__projects[item]

    def __str__(self):
        return str([
            project.get_name()
            for project
            in self.__projects
        ])

    @classmethod
    def from_names(cls, project_names):
        result = cls()
        result.__projects = [
            Project(name)
            for name in project_names if isinstance(name, str)
        ]
        return result

    @classmethod
    def from_projects(cls, projects):
        result = cls()
        result.__projects = [
            project
            for project in projects if isinstance(project, Project)
        ]
        return result

    @classmethod
    def from_dir(cls, directory='.'):
        return cls.from_projects([
            Project.from_file_name(file_name)
            for file_name in os.listdir(directory)
        ])

    @classmethod
    def from_args(cls, args):
        if args is not None and 'projects' in args:
            if isinstance(args.projects, list) and args.projects:
                return cls.from_names(args.projects)

            elif isinstance(args.projects, str):
                return cls.from_names([args.projects])

        return cls()

    def empty(self):
        return not self.__projects

    def filter_exists(self):
        result = Projects()
        result.__projects = [
            project
            for project in self.__projects
            if project.exists()
        ]
        return result

    def filter_enabled(self):
        result = Projects()
        result.__projects = [
            project
            for project in self.__projects
            if project.is_enabled()
        ]
        return result

    def filter_disabled(self):
        result = Projects()
        result.__projects = [
            project
            for project in self.__projects
            if project.is_disabled()
        ]
        return result
