#!/usr/bin/env python3
import logging

import kiwi


def set_verbosity(logger, handler, verbosity):
    if verbosity >= 2:
        log_level = logging.DEBUG
        log_format = "[%(asctime)s] %(levelname)s @ %(filename)s:%(funcName)s:%(lineno)d: %(message)s"
    elif verbosity >= 1:
        log_level = logging.INFO
        log_format = "[%(asctime)s] %(levelname)s: %(message)s"
    else:
        log_level = logging.WARNING
        log_format = "%(levelname)s: %(message)s"

    logger.setLevel(log_level)
    handler.setFormatter(logging.Formatter(log_format))


def main():
    log_handler = logging.StreamHandler()
    logging.getLogger().addHandler(log_handler)
    set_verbosity(logging.getLogger(), log_handler, kiwi.verbosity())

    kiwi.run()


if __name__ == "__main__":
    main()
