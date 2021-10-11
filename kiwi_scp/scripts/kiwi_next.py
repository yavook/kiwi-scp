from kiwi_scp.config import Config
import yaml


def main():
    with open("./kiwi_scp/data/etc/kiwi_default.yml") as kc:
        yml = yaml.safe_load(kc)
        kiwi = Config(**yml)

        print(repr(kiwi))


if __name__ == "__main__":
    main()
