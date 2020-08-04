import os
import yaml



class Config:
    __content = None

    def __init__(self, filename):
        with open(filename, 'r') as stream:
            try:
                self.__content = yaml.safe_load(stream)
                print(self.__content)

            except yaml.YAMLError as exc:
                print(exc)

    @classmethod
    def default(cls):
        kiwi_root = os.environ.get('KIWI_ROOT')

        cfg = cls(kiwi_root + "/default.kiwi.yml")
        with open(kiwi_root + "/version-tag", 'r') as stream:
            cfg.__content["version"] = stream.read().strip()

        return cfg

    def __user_input(self, path, key, prompt):
        content = self.__content

        for step in path:
            content = content[step]

        try:
            result = input("{} [Default: {}] ".format(prompt, content[key])).strip()
        except:
            result = None

        if result:
            content[key] = result

    def init(self):
        self.__user_input([], "version", "Choose kiwi-config version")

        self.__user_input(["suffix"], "project", "Enter suffix for project directories")
        self.__user_input(["suffix"], "down", "Enter suffix for disabled projects")

        self.__user_input(["docker"], "net", "Enter ")
        self.__user_input(["docker"], "cidr", "Enter ")

        self.__user_input(["target"], "root", "Enter ")
