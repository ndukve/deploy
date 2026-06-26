#!/bin/sh
set -eu

IMAGE_TAG="local/cryptpad-sso-test"

docker build -f docker/cryptpad/Dockerfile -t "${IMAGE_TAG}" .
docker run --rm "${IMAGE_TAG}" sh -lc '
  test -d /cryptpad/lib/plugins/sso &&
  test -f /cryptpad/config/sso.js &&
  mkdir -p /cryptpad/data/decrees &&
  /usr/local/bin/cryptpad-entrypoint.sh true &&
  grep -q "\"SET_BEARER_SECRET\"" /cryptpad/data/decrees/decree.ndjson
'
