#!/bin/sh
set -eu

TARGET_UID="${CPAD_UID:-4001}"
TARGET_GID="${CPAD_GID:-4001}"

mkdir -p \
  /work/volumes/cryptpad/blob \
  /work/volumes/cryptpad/block \
  /work/volumes/cryptpad/data \
  /work/volumes/cryptpad/files \
  /work/volumes/postgres/data \
  /work/volumes/rmcryptpad/oidc \
  /work/volumes/nginx/certs

chown -R "${TARGET_UID}:${TARGET_GID}" /work/volumes/cryptpad
chown -R "${TARGET_UID}:${TARGET_GID}" /work/volumes/postgres /work/volumes/rmcryptpad
find /work/volumes/cryptpad -type d -exec chmod 0775 {} +
find /work/volumes/cryptpad -type f -exec chmod 0664 {} +
find /work/volumes/rmcryptpad -type d -exec chmod 0775 {} +
find /work/volumes/rmcryptpad -type f -exec chmod 0664 {} +
chmod 0700 /work/volumes/postgres /work/volumes/postgres/data
chmod 0755 /work/volumes/nginx /work/volumes/nginx/certs
