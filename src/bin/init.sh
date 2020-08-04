#!/bin/bash

source "${KIWI_ROOT}/inc/functions.sh"

# read default baseconfig
conf_VERSION="${KIWI_VERSION}"
read_kiwi_config "${KIWI_ROOT}/etc/default.${KIWI_CONF_NAME}"

# if pwd is a kiwi folder, read local baseconfig
if [ -f "./${KIWI_CONF_NAME}" ]; then
    echo "[WARN] Overwriting existing '${KIWI_CONF_NAME}'"
    read_kiwi_config "./${KIWI_CONF_NAME}"
fi

function user_input() {
    local prompt="${1}"
    local varname="${2}"

    local input
    read -p "${prompt} [Default '${!varname}']: " input

    eval "${varname}='${input:-${!varname}}'"
}

declare -A config_explain
config_explain=(
    [VERSION]="kiwi-config version"
    [SUFFIX_PROJECT]="suffix for project directories"
    [SUFFIX_DOWN]="suffix for disabled projects"
)

for varname in "${!config_explain[@]}"; do
    echo "${varname}"
    user_input "Enter ${config_explain[${varname}]}" conf_${varname}
done

exit 0

user_input "Choose kiwi-config version" conf_VERSION

user_input "Enter suffix for project directories" conf_SUFFIX_PROJECT
user_input "Enter suffix for disabled projects" conf_SUFFIX_DOWN

user_input "Enter suffix for disabled projects" conf_SUFFIX_DOWN
user_input "Enter suffix for disabled projects" conf_SUFFIX_DOWN

user_input "Enter suffix for disabled projects" conf_SUFFIX_DOWN

echo "conf_VERSION: ${conf_VERSION}"
echo "conf_SUFFIX_PROJECT: ${conf_SUFFIX_PROJECT}"

exit 0

read -p "Choose kiwi-config version [Default '${conf_version}']: " kiwi_VERSION
conf_VERSION=${kiwi_VERSION:-${conf_VERSION}}

read -p "suffix for kiwi-config version to use [Default '${conf_version}']: " kiwi_suffix_project

echo "conf_VERSION: ${conf_VERSION}"