#!/bin/bash
if [ -z "$RMMTX_PASSWORD" ]
then
  echo "RMMTX_PASSWORD not set"
  exit 1
fi
set -e
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER rmmtxauthz WITH ENCRYPTED PASSWORD '$RMMTX_PASSWORD';
    CREATE DATABASE rmmtxauthz;
    GRANT ALL PRIVILEGES ON DATABASE rmmtxauthz TO rmmtxauthz;
EOSQL
