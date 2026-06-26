#!/bin/bash

# Run the init-scripts
if [ -d /docker-entrypoint-initdb.d ]
then
  for file in /docker-entrypoint-initdb.d/*
  do
    [ -f "$file" ] && [ -x "$file" ] && "$file"
  done
fi

# Run the 'exec' command as the last step of the script.
# As it replaces the current shell process, no additional shell commands will run after the 'exec' command.
exec /opt/keycloak/bin/kc.sh "$@" ${KC_EXTRA_ARGS}
