#!/usr/bin/env -S /bin/bash
set -e

. /cfssl-init.sh

#
# Run cfssl services
#
pushd "${CFSSL_PERSISTENT_FOLDER}" > /dev/null
echo "$(date) --- Starting sqlite goose addong"
goose -dir certdb/sqlite/migrations sqlite3 certstore_development.db up
echo "$(date) --- Running 'cfssl ocspserve'"
cfssl ocspserve -address=$CFSSL_BIND_ADDRESS -port $CFSSL_OCSP_BIND_PORT \
      -db-config "${RUN_DB_CONFIG}" \
      -loglevel 0

#
# Exit/restart/crash
#
echo "$(date) --- ocsp-start.sh finished"
