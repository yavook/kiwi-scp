# system
import os


#############
# ENVIRONMENT

# location of "src" directory to use
KIWI_ROOT = os.getenv('KIWI_ROOT', ".")
# default name of kiwi-config file
KIWI_CONF_NAME = os.getenv('KIWI_CONF_NAME', "kiwi.yml")


############
# FILE NAMES

# text files inside kiwi-config "src" directory
HEADER_KIWI_CONF_NAME = f"{KIWI_ROOT}/etc/kiwi_header.yml"
DEFAULT_KIWI_CONF_NAME = f"{KIWI_ROOT}/etc/kiwi_default.yml"
VERSION_TAG_NAME = f"{KIWI_ROOT}/etc/version_tag"

# special config directory in projects
CONF_DIRECTORY_NAME = 'conf'
# location for auxiliary Dockerfiles
IMAGES_DIRECTORY_NAME = f"{KIWI_ROOT}/images"


####################
# DOCKER IMAGE NAMES

# name for auxiliary docker images
LOCAL_IMAGES_NAME = 'localhost/kiwi-config/auxiliary'
DEFAULT_IMAGE_NAME = 'alpine:latest'
