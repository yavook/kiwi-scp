#!/bin/sh

#############
# CONSTANTS #
#############

# default installation directory
INSTALL_DIR_DEFAULT="/usr/local/sbin"
# URI of "kiwi" launcher script
KIWI_URI="https://raw.githubusercontent.com/ldericher/kiwi-scp/master/kiwi"

#############
# FUNCTIONS #
#############

# prompt yes/no question (default yes)
yes_no() {
  # prompt and read from terminal
  printf "%s [Y|n] " "${1}"
  read -r answer </dev/tty || answer=""

  # check first character
  answer="$(printf '%.1s' "${answer}")"
  if [ "${answer}" = "N" ] || [ "${answer}" = "n" ]; then
    # negative
    return 1
  else
    # positive
    return 0
  fi
}

# exit with error
die() {
  echo "ERROR: ${1}!" >/dev/stderr
  exit 1
}

########
# MAIN #
########

# check if already installed
install_kiwi="$(command -v kiwi)"

if [ -x "${install_kiwi}" ]; then
  # kiwi is installed: Choose that directory
  install_dir="$(dirname "${install_kiwi}")"

  if ! yes_no "kiwi executable found in '${install_dir}'. Overwrite?"; then
    die "Uninstall existing '${install_kiwi}' first"
  fi

elif [ ${#} -gt 0 ]; then
  # install dir candidate given as CLI argument
  install_dir="${1}"
  shift 1
fi

# check dir given by argument
while [ ! -d "${install_dir}" ]; do
  # prompt user for installation directory
  printf "Select installation directory [Default: '%s']: " "${INSTALL_DIR_DEFAULT}"
  read -r install_dir </dev/tty || install_dir="${INSTALL_DIR_DEFAULT}"
  install_dir="${install_dir:-${INSTALL_DIR_DEFAULT}}"

  # check dir given on terminal
  if [ ! -d "${install_dir}" ]; then
    # fail if install dir can't be created
    if yes_no "Install directory doesn't exist. Try creating?"; then
      if ! mkdir -p "${install_dir}" >/dev/null 2>/dev/null; then
        die "Couldn't create install directory"
      fi
    fi
  fi
done

# start actual installation
printf "Installing into '%s' ... " "${install_dir}"
tmp_file="$(mktemp)"

if ! curl --proto '=https' --tlsv1.2 -sSf -o "${tmp_file}" "${KIWI_URI}" >/dev/null 2>/dev/null; then
  rm "${tmp_file}"
  die "Downloading 'kiwi' failed"
fi

if ! install -m 0755 "${tmp_file}" "${install_dir}/kiwi" >/dev/null 2>/dev/null; then
  rm "${tmp_file}"
  die "Installing 'kiwi' failed"
fi

# finalization
rm "${tmp_file}"
echo "OK"
exit 0
