#!/usr/bin/env python3

import argparse
from kiwi.config import *


def main():
    parser = argparse.ArgumentParser(description='kiwi-config')

    subs = parser.add_subparsers()
    subs.required = True
    subs.dest = 'command'

    subs.add_parser('init', help="Create new kiwi-config instance")
    subs.add_parser('add', help="Add a project to kiwi-config")

    # parser.add_argument('cmd', metavar='command', type=str, help='subcommand to execute')

    args = parser.parse_args()
    print(args.command)

    cf = Config.default()
    # cf.user_input()
    cf.dump()

    pass


if __name__ == "__main__":
    main()
