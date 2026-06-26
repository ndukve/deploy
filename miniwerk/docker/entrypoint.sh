#!/bin/bash -l
set -e
if [ "$#" -eq 0 ]; then
  miniwerk -vv init
else
  exec "$@"
fi
