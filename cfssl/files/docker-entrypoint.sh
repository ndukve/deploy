#!/usr/bin/env -S /bin/bash
set -e
. /container-env.sh
if [ "$#" -eq 0 ]; then
  if [ "$CFSSL_MODE" == "api" ]; then
    . /cfssl-start.sh
  fi
  if [ "$CFSSL_MODE" == "ocsp" ]; then
    . /ocsp-start.sh
  fi
else
  # run the given command
  exec "$@"
fi
