from kiwi_scp.config import Config
import yaml


def main():
    with open("./example/kiwi.yml") as kc:
        yml = yaml.safe_load(kc)
        kiwi = Config(**yml)

        print(repr(kiwi))

    kiwi = Config()
    print(repr(kiwi))


if __name__ == "__main__":
    main()
