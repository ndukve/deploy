#!/usr/bin/env -S /bin/bash
set -e
. /container-env.sh
if [ "$#" -eq 0 ]; then
  PORT=$(ocsprest config | jq .port)
  ocsprest -v refresher &
  gunicorn "ocsprest.routes:app_w_logging()" --bind 0.0.0.0:$PORT -w 4 --worker-class uvicorn.workers.UvicornWorker
else
  # run the given command
  exec "$@"
fi
