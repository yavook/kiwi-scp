#!/usr/bin/env python3

import kiwi
from kiwi.cmd_init import InitSubCommand

def main():
    isc = InitSubCommand()
    isc.setup()

    args = kiwi.Parser.get_args()
    print(args.command)

    isc.run()

    pass


if __name__ == "__main__":
    main()
