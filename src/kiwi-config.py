#!/usr/bin/env python3

import argparse
from kiwi import *


def main():
    parser = argparse.ArgumentParser(description='kiwi-config')
    parser.add_argument('cmd', metavar='command', type=str, help='subcommand to execute')

    args = parser.parse_args()
    print(args.cmd)

    cf = config.Config.default()

    pass


if __name__ == "__main__":
    main()
