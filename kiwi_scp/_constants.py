# system
import os

#############
# REGEX PARTS

# regex part for a number with no leading zeroes
_RE_NUMBER: str = r"[0-9]|[1-9][0-9]*"

# regex for a semantic version string
RE_SEMVER = rf"^{_RE_NUMBER}(?:\.{_RE_NUMBER}(?:\.{_RE_NUMBER})?)?$"

# regex for a lowercase variable name
RE_VARNAME = r"^[A-Za-z](?:[A-Za-z0-9_-]*[A-Za-z0-9])$"

#############
# ENVIRONMENT

# location of "kiwi_scp" module
KIWI_ROOT = os.path.dirname(__file__)
# default name of kiwi-scp file
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")

############
# FILE NAMES

# text files inside kiwi-scp "src" directory
HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/data/etc/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/data/etc/kiwi_default.yml"
VERSION_TAG_NAME = f"{KIWI_ROOT}/data/etc/version_tag"
DEFAULT_DOCKER_COMPOSE_NAME = f"{KIWI_ROOT}/data/etc/docker-compose_default.yml"
KIWI_HELP_TEXT_NAME = f"{KIWI_ROOT}/data/etc/kiwi_help.txt"
COMMAND_HELP_TEXT_NAME = f"{KIWI_ROOT}/data/etc/command_help.txt"

# special config directory in projects
CONF_DIRECTORY_NAME = 'conf'
# location for auxiliary Dockerfiles
IMAGES_DIRECTORY_NAME = f"{KIWI_ROOT}/data/images"

####################
# DOCKER IMAGE NAMES

# name for auxiliary docker images
LOCAL_IMAGES_NAME = 'localhost/kiwi-scp/auxiliary'
DEFAULT_IMAGE_NAME = 'alpine:latest'