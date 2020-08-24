#!/bin/sh

#############
# CONSTANTS #
#############

# dependencies to run kiwi-config
KIWI_DEPS="bash python3 pipenv less"

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
install_dir_default="/usr/local/bin"
valid="no"

while [ "${valid}" = "no" ]; do
  printf "Select installation directory [Default: '%s']: " "${install_dir_default}"
  read install_dir </dev/tty || install_dir="${install_dir_default}"
  install_dir="${install_dir:-${install_dir_default}}"

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

if ! curl --proto '=https' --tlsv1.2 --silent --fail --output "${tmp_file}" "${uri}" >/dev/null 2>/dev/null; then
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
