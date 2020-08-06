import os
import re
import yaml


class Config:
    KIWI_ROOT = os.getenv('KIWI_ROOT', '.')
    __yml_content = None

    @classmethod
    def __from_file(cls, filename):
        result = cls()

        with open(filename, 'r') as stream:
            try:
                result.__yml_content = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return result

    @classmethod
    def default(cls):
        result = cls.__from_file(cls.KIWI_ROOT + "/default.kiwi.yml")

        with open(cls.KIWI_ROOT + "/version-tag", 'r') as stream:
            result.__yml_content["version"] = stream.read().strip()

        return result

    def __yml_resolve(self, key):
        # "a:b:c" => path = ['a', 'b'], key = 'c'
        path = key.split(':')
        path, key = path[:-1], path[-1]

        # resolve path
        content = self.__yml_content
        for step in path:
            content = content[step]

        return content, key

    def __yml_get(self, key):
        content, key = self.__yml_resolve(key)
        return content[key]

    def __yml_set(self, key, value):
        content, key = self.__yml_resolve(key)
        content[key] = value

    def __user_input(self, key, prompt):
        # prompt user as per argument
        result = input("{} [Current: {}] ".format(prompt, self.__yml_get(key))).strip()

        # store result if present
        if result:
            self.__yml_set(key, result)

    def user_input(self):
        self.__user_input("version", "Choose kiwi-config version")

        self.__user_input("markers:project", "Enter marker string for project directories")
        self.__user_input("markers:down", "Enter marker string for disabled projects")

        self.__user_input("network:name", "Enter name for local docker network")
        self.__user_input("network:cidr", "Enter CIDR block for local docker network")

        self.__user_input("runtime:storage", "Enter main directory for local data")

    def dump(self):
        yml_string = yaml.dump(self.__yml_content, default_flow_style=False, sort_keys=False)
        yml_string = re.sub(r'^(\S)', r'\n\1', yml_string, flags=re.MULTILINE)

        with open(Config.KIWI_ROOT + "/default.kiwi.yml", 'r') as stream:
            yml_header = stream.read().strip()
            yml_header = re.sub(r'^[^#].*', r'', yml_header, flags=re.MULTILINE).strip()
            yml_string = "{}\n{}".format(yml_header, yml_string)

        print(yml_string)
