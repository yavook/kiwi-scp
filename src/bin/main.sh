#!/bin/bash

command="${1}"
shift 1

case "${command}" in
   "init")
      exec "${KIWI_ROOT}/bin/${command}.sh" "${@}"
      ;;
   *)
      echo "Unknown kiwi command '${command}'."
      exit 1
      ;;
esac