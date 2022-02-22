import os

#############
# REGEX PARTS

# regex part for a number with no leading zeroes
_RE_NUMBER: str = r"(?:0|[1-9][0-9]*)"

# regex for a semantic version string
RE_SEMVER = rf"^{_RE_NUMBER}(?:\.{_RE_NUMBER}(?:\.{_RE_NUMBER})?)?$"

# regex for a variable name
RE_VARNAME = r"^[A-Za-z](?:[A-Za-z0-9\._-]*[A-Za-z0-9])$"

#############
# ENVIRONMENT

# location of "kiwi_scp" module
KIWI_ROOT = os.path.dirname(__file__)
# default name of kiwi-scp file
KIWI_CONF_NAME = os.getenv("KIWI_CONF_NAME", "kiwi.yml")
# default name of compose files
COMPOSE_FILE_NAME = "docker-compose.yml"

############
# FILE NAMES

# text files inside kiwi-scp "src" directory
HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/data/etc/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/data/etc/kiwi_default.yml"
DEFAULT_DOCKER_COMPOSE_NAME = f"{KIWI_ROOT}/data/etc/docker-compose_default.yml"

# special config directory
CONFIG_DIRECTORY_NAME = "config"

# location for auxiliary Dockerfiles
IMAGES_DIRECTORY_NAME = f"{KIWI_ROOT}/data/images"

# prohibited project names
RESERVED_PROJECT_NAMES = [
    CONFIG_DIRECTORY_NAME,
]

####################
# DOCKER IMAGE NAMES

# name for auxiliary docker images
LOCAL_IMAGES_NAME = "localhost/kiwi-scp/auxiliary"
DEFAULT_IMAGE_NAME = "alpine:latest"
