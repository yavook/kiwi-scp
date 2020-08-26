# system
import os


#############
# ENVIRONMENT

# location of "src" directory to use
KIWI_ROOT = os.getenv('KIWI_ROOT', ".")
# default name of kiwi-scp file
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")


############
# FILE NAMES

# text files inside kiwi-scp "src" directory
HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/etc/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/etc/kiwi_default.yml"
VERSION_TAG_NAME = f"{KIWI_ROOT}/etc/version_tag"
DEFAULT_DOCKER_COMPOSE_NAME = f"{KIWI_ROOT}/etc/docker-compose_default.yml"
KIWI_HELP_TEXT_NAME = f"{KIWI_ROOT}/etc/kiwi_help.txt"
COMMAND_HELP_TEXT_NAME = f"{KIWI_ROOT}/etc/command_help.txt"

# special config directory in projects
CONF_DIRECTORY_NAME = 'conf'
# location for auxiliary Dockerfiles
IMAGES_DIRECTORY_NAME = f"{KIWI_ROOT}/images"


####################
# DOCKER IMAGE NAMES

# name for auxiliary docker images
LOCAL_IMAGES_NAME = 'localhost/kiwi-scp/auxiliary'
DEFAULT_IMAGE_NAME = 'alpine:latest'
