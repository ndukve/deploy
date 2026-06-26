#!/bin/sh
set -eu

/usr/local/bin/generate-local-cert.sh

exec "$@"
