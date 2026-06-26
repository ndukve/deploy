#!/bin/sh
set -eu

CPAD_CONF="${CPAD_CONF:-/cryptpad/config/config.js}"
CPAD_EXTRA_CA_TARGET="${NODE_EXTRA_CA_CERTS:-/tmp/cryptpad-extra-ca.pem}"
CPAD_DECREE_DIR="${CPAD_DECREE_DIR:-/cryptpad/data/decrees}"
CPAD_DECREE_FILE="${CPAD_DECREE_FILE:-${CPAD_DECREE_DIR}/decree.ndjson}"

if [ -n "${NODE_EXTRA_CA_CERTS:-}" ]; then
  found_extra_ca=0
  : > "$CPAD_EXTRA_CA_TARGET"
  for cert in /ca_public/miniwerk_ca.pem /ca_public/ca_chain.pem; do
    if [ ! -f "$cert" ]; then
      continue
    fi
    cat "$cert" >> "$CPAD_EXTRA_CA_TARGET"
    printf '\n' >> "$CPAD_EXTRA_CA_TARGET"
    found_extra_ca=1
  done
  if [ "$found_extra_ca" -eq 0 ]; then
    rm -f "$CPAD_EXTRA_CA_TARGET"
    unset NODE_EXTRA_CA_CERTS
  fi
fi

if [ ! -f "$CPAD_CONF" ]; then
  echo "CryptPad config missing at $CPAD_CONF, copying the upstream example." >&2
  cp /cryptpad/config/config.example.js "$CPAD_CONF"
fi

# ── loginSalt: generate once, persist in data volume ─────────────────────────
CPAD_SALT_FILE="/cryptpad/data/.login-salt"
if [ ! -f "$CPAD_SALT_FILE" ]; then
  node -e "process.stdout.write(require('crypto').randomBytes(32).toString('hex'))" > "$CPAD_SALT_FILE"
  echo "Generated new loginSalt (stored in $CPAD_SALT_FILE)" >&2
fi
LOGIN_SALT="$(cat "$CPAD_SALT_FILE")"

# ── Assemble /cryptpad/customize from read-only source with salt injected ────
CPAD_CUSTOMIZE_SRC="/cryptpad/customize.local"
if [ -d "$CPAD_CUSTOMIZE_SRC" ]; then
  cp -a "$CPAD_CUSTOMIZE_SRC"/. /cryptpad/customize/
  if [ -f /cryptpad/customize/application_config.js ]; then
    sed -i "s/__LOGIN_SALT__/${LOGIN_SALT}/" /cryptpad/customize/application_config.js
    echo "Injected loginSalt into application_config.js" >&2
  fi
fi

mkdir -p "$CPAD_DECREE_DIR"
if [ ! -f "$CPAD_DECREE_FILE" ] || ! grep -q '"SET_BEARER_SECRET"' "$CPAD_DECREE_FILE"; then
  bearer_secret="$(node -e "process.stdout.write(require('crypto').randomBytes(32).toString('base64'))")"
  decree_time="$(node -e "process.stdout.write(String(Date.now()))")"
  node -e "
    const fs = require('node:fs');
    const decreeFile = process.argv[1];
    const bearerSecret = process.argv[2];
    const decreeTime = Number(process.argv[3]);
    const decree = ['SET_BEARER_SECRET', [bearerSecret], 'INTERNAL', decreeTime];
    fs.appendFileSync(decreeFile, JSON.stringify(decree) + '\n');
  " "$CPAD_DECREE_FILE" "$bearer_secret" "$decree_time"
fi

exec "$@"
