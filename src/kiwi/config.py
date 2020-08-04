class Config:
    # version, suffix_project, suffix_down, docker_net, docker_cidr, target_root = None

    def __init__(self, filename):
        import yaml

        with open(filename, 'r') as stream:
            try:
                print(yaml.safe_load(stream))
            except yaml.YAMLError as exc:
                print(exc)

    @classmethod
    def default(cls):
        return cls("./etc/default.kiwi.yml")
