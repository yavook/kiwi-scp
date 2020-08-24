#!/bin/sh

#############
# CONSTANTS #
#############

# dependencies to run kiwi-config
KIWI_DEPS="bash python3 pipenv less"
# default install directory
INSTALL_DIR_DEFAULT="/usr/local/bin"

##########
# CHECKS #
##########

printf "checking dependencies ... "

for dep in ${KIWI_DEPS}; do
  printf "%s, " "${dep}"

  if ! command -v "${dep}" >/dev/null 2>/dev/null; then
    echo
    echo "Dependency '${dep}' not found, please install!" >/dev/stderr
    exit 1
  fi
done

echo "OK"

########
# MAIN #
########

# prompt for installation directory
valid="no"

while [ "${valid}" = "no" ]; do
  printf "Select installation directory [Default: '%s']: " "${INSTALL_DIR_DEFAULT}"
  read install_dir </dev/tty || install_dir="${INSTALL_DIR_DEFAULT}"
  install_dir="${install_dir:-${INSTALL_DIR_DEFAULT}}"

  # check
  if [ -d "${install_dir}" ]; then
    valid="yes"

  else
    printf "Install directory doesn't exist. Try creating? [Y|n] "
    read yesno </dev/tty || yesno="yes"
    if [ ! "${yesno}" = "N" ] || [ ! "${yesno}" = "n" ]; then

      # check creation failure
      if mkdir -p "${install_dir}"; then
        valid="yes"

      else
        echo "Invalid install directory." >/dev/stderr
        exit 1
      fi
    fi
  fi
done

# start actual installation
printf "Installing into '%s' ... " "${install_dir}"

# install "kiwi" script
uri="https://raw.githubusercontent.com/ldericher/kiwi-config/master/kiwi"
tmp_file="$(mktemp)"

if ! curl --proto '=https' --tlsv1.2 -sSf -o "${tmp_file}" "${uri}" >/dev/null 2>/dev/null; then
  rm "${tmp_file}"
  echo "Download 'kiwi' failed!" >/dev/stderr
  exit 1
fi

if ! install -m 0755 "${tmp_file}" "${install_dir}/kiwi" >/dev/null 2>/dev/null; then
  rm "${tmp_file}"
  echo "Install 'kiwi' failed!" >/dev/stderr
  exit 1
fi

rm "${tmp_file}"

# finalization
echo "OK"
exit 0
