import os
import yaml


class Config:
    KIWI_ROOT = os.getenv('KIWI_ROOT', '.')
    __ymlContent = None

    def __init__(self):


    @classmethod
    def __from_file(cls, filename):
        with open(filename, 'r') as stream:
            try:
                self.__ymlContent = yaml.safe_load(stream)

            except yaml.YAMLError as exc:
                print(exc)

    @classmethod
    def default(cls):
        result = cls.__from_file(cls.KIWI_ROOT + "/default.kiwi.yml")

        with open(cls.KIWI_ROOT + "/version-tag", 'r') as stream:
            result.__ymlContent["version"] = stream.read().strip()

        return result

    def __user_input(self, key, prompt):
        """"""

        # "a:b:c" => path = ['a', 'b'], key = 'c'
        path = key.split(':')
        (path, key) = (path[:-1], path[-1])

        # resolve path
        content = self.__ymlContent
        for step in path:
            content = content[step]

        # prompt user as per argument
        result = input("{} [Default: {}] ".format(prompt, content[key])).strip()

        #
        if result:
            content[key] = result

    def user_input(self):
        self.__user_input("version", "Choose kiwi-config version")

        self.__user_input("suffixes:project", "Enter suffix for project directories")
        self.__user_input("suffixes:down", "Enter suffix for disabled projects")

        self.__user_input("network:name", "Enter name for docker network")
        self.__user_input("network:cidr", "Enter ")

        self.__user_input("storage:location", "Enter ")
