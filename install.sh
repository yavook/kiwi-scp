#!/bin/sh

#############
# CONSTANTS #
#############

# default installation directory
INSTALL_DIR_DEFAULT="/usr/local/bin"


############
# CLI ARGS #
############

# installation directory
install_dir="${1}"
# adjust default if given
INSTALL_DIR_DEFAULT="${1:-${INSTALL_DIR_DEFAULT}}"


########
# MAIN #
########

# prompt for installation directory
while [ ! -d "${install_dir}" ]; do
  printf "Select installation directory [Default: '%s']: " "${INSTALL_DIR_DEFAULT}"
  read -r install_dir </dev/tty || install_dir="${INSTALL_DIR_DEFAULT}"
  install_dir="${install_dir:-${INSTALL_DIR_DEFAULT}}"

  # check if given dir exists
  if [ ! -d "${install_dir}" ]; then
    printf "Install directory doesn't exist. Try creating? [Y|n] "
    read -r yesno </dev/tty || yesno="yes"
    yesno=$(printf '%.1s' "${yesno}")

    if [ ! "${yesno}" = "N" ] && [ ! "${yesno}" = "n" ]; then
      # fail this script if we can't create the install dir
      if ! mkdir -p "${install_dir}"; then
        echo "Invalid install directory." >/dev/stderr
        exit 1
      fi
    fi
  fi
done

if [ ! -d "${install_dir}" ]; then
  echo "wtf?"
  exit 1
fi

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
