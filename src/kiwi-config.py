#!/usr/bin/env python3

# system
import logging

# local
import kiwi


def set_verbosity(logger, handler, verbosity):
    """set logging default verbosity level and format"""

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
    # add a new handler (needed to set the level)
    log_handler = logging.StreamHandler()
    logging.getLogger().addHandler(log_handler)
    set_verbosity(logging.getLogger(), log_handler, kiwi.verbosity())

    # run the app
    kiwi.run()


if __name__ == "__main__":
    main()
