#!/usr/bin/env python3
import logging

import kiwi
from kiwi.subcommands import *


def main():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.NOTSET
    )

    commands = [
        InitCommand,
        ShowCommand,
        LogsCommand
    ]

    for cmd in commands:
        cmd.setup()

    args = kiwi.Parser.get_args()

    if args.verbose >= 2:
        log_level = logging.DEBUG
    elif args.verbose >= 1:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING

    logging.getLogger().setLevel(log_level)

    for cmd in commands:
        if cmd.command == args.command:
            cmd.run()
            return


if __name__ == "__main__":
    main()
