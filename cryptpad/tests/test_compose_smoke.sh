#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP_DIR="$(mktemp -d)"
WORK_DIR="${TMP_DIR}/repo"
PROJECT_NAME="cryptpad-smoke-$$"
PORT="${CPAD_HTTPS_PORT:-18443}"

log() {
  printf '%s\n' "$*"
}

print_json() {
  python3 - "$1" <<'PY'
import json
import sys

print(json.dumps(json.loads(sys.argv[1]), indent=2, sort_keys=True))
PY
}

redact_token() {
  python3 - "$1" <<'PY'
import sys

value = sys.argv[1]
prefix = value[:8]
suffix = value[-8:] if len(value) > 8 else value
print(f"{prefix}...{suffix} (len={len(value)})")
PY
}

cleanup() {
  status=$?
  if [ -f "${WORK_DIR}/compose.yaml" ]; then
    if [ "${status}" -ne 0 ]; then
      (
        cd "${WORK_DIR}"
        docker compose -p "${PROJECT_NAME}" logs --no-color || true
      )
    fi
    (
      cd "${WORK_DIR}"
      docker compose -p "${PROJECT_NAME}" down -v --remove-orphans || true
    )
  fi
  if [ -d "${TMP_DIR}" ]; then
    docker run --rm -v "${TMP_DIR}:/work" alpine:3.21 sh -c 'rm -rf /work/*' >/dev/null 2>&1 || true
    rm -rf "${TMP_DIR}"
  fi
  exit "${status}"
}

trap cleanup EXIT INT TERM

if ! command -v rsync >/dev/null 2>&1; then
  echo "rsync is required for the standalone compose smoke test" >&2
  exit 1
fi

rsync -a \
  --exclude '.git' \
  --exclude '.env' \
  --exclude '.worktrees' \
  --exclude 'volumes' \
  --exclude 'rmcryptpad/.pytest-oidc' \
  --exclude 'rmcryptpad/.pytest_cache' \
  --exclude 'rmcryptpad/ui/node_modules' \
  --exclude 'rmcryptpad/ui/dist' \
  "${ROOT_DIR}/" "${WORK_DIR}/"

cd "${WORK_DIR}"

python3 - "${WORK_DIR}/docker/nginx/nginx.conf" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
text = path.read_text(encoding="utf-8")
old = """  server {
    listen 443 ssl;
    listen [::]:443 ssl;
    http2 on;
    server_name _;
"""
new = """  server {
    listen 443 ssl default_server;
    listen [::]:443 ssl default_server;
    http2 on;
    server_name _;
"""
if old not in text:
    raise SystemExit("expected standalone nginx cryptpad vhost block not found")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
PY
log "Applied standalone nginx default-server tweak in the temporary smoke-test copy"

export CPAD_HTTPS_PORT="${PORT}"
export CPAD_MAIN_DOMAIN="https://cryptpad.localhost:${PORT}"
export CPAD_SANDBOX_DOMAIN="https://sandbox.cryptpad.localhost:${PORT}"
export CPAD_SSO_ISSUER="https://rmcryptpad.localhost:${PORT}"
export RMCRYPTPAD_PUBLIC_URL="${CPAD_MAIN_DOMAIN}"
export RMCRYPTPAD_PUBLIC_SANDBOX_URL="${CPAD_SANDBOX_DOMAIN}"
export RMCRYPTPAD_OIDC_ISSUER="${CPAD_SSO_ISSUER}"

docker compose -p "${PROJECT_NAME}" config >/dev/null
docker compose -p "${PROJECT_NAME}" up -d --build --wait

TLS_CERT="${WORK_DIR}/volumes/nginx/certs/cryptpad.local.pem"

curl_status() {
  local host="$1"
  local url="$2"
  local extra=("${@:3}")
  curl -sS \
    --connect-timeout 5 \
    --max-time 15 \
    --cacert "${TLS_CERT}" \
    --resolve "${host}:${PORT}:127.0.0.1" \
    -o /dev/null \
    -w '%{http_code}' \
    "${extra[@]}" \
    "${url}"
}

wait_for_http() {
  local host="$1"
  local url="$2"
  local _attempt status
  for _attempt in $(seq 1 30); do
    status="$(curl_status "${host}" "${url}" || true)"
    case "${status}" in
      200|301|302|303)
        return 0
        ;;
    esac
    sleep 2
  done
  echo "Timed out waiting for ${url}" >&2
  return 1
}

curl_body() {
  local host="$1"
  local url="$2"
  local extra=("${@:3}")
  curl -sS \
    --connect-timeout 5 \
    --max-time 15 \
    --cacert "${TLS_CERT}" \
    --resolve "${host}:${PORT}:127.0.0.1" \
    "${extra[@]}" \
    "${url}"
}

wait_for_http "cryptpad.localhost" "https://cryptpad.localhost:${PORT}/"
wait_for_http "sandbox.cryptpad.localhost" "https://sandbox.cryptpad.localhost:${PORT}/"
wait_for_http "rmcryptpad.localhost" "https://rmcryptpad.localhost:${PORT}/.well-known/openid-configuration"
wait_for_http "rmcryptpad.localhost" "https://rmcryptpad.localhost:${PORT}/ui/cryptpad/remoteEntry.js"

main_status="$(curl_status "cryptpad.localhost" "https://cryptpad.localhost:${PORT}/")"
log "GET https://cryptpad.localhost:${PORT}/ -> ${main_status}"
main_page="$(curl_body "cryptpad.localhost" "https://cryptpad.localhost:${PORT}/")"
printf '%s' "${main_page}" | grep -q 'CryptPad'
log "Main page contains: CryptPad"

sandbox_status="$(curl_status "sandbox.cryptpad.localhost" "https://sandbox.cryptpad.localhost:${PORT}/")"
log "GET https://sandbox.cryptpad.localhost:${PORT}/ -> ${sandbox_status}"

discovery_status="$(curl_status "rmcryptpad.localhost" "https://rmcryptpad.localhost:${PORT}/.well-known/openid-configuration")"
log "GET https://rmcryptpad.localhost:${PORT}/.well-known/openid-configuration -> ${discovery_status}"
discovery_json="$(curl_body "rmcryptpad.localhost" "https://rmcryptpad.localhost:${PORT}/.well-known/openid-configuration")"
log "Discovery response:"
print_json "${discovery_json}"
python3 - "${PORT}" "${discovery_json}" <<'PY'
import json
import sys

port = sys.argv[1]
payload = json.loads(sys.argv[2])
assert payload["issuer"] == f"https://rmcryptpad.localhost:{port}"
assert payload["authorization_endpoint"].endswith("/oidc/authorize")
assert payload["token_endpoint"].endswith("/oidc/token")
assert payload["userinfo_endpoint"].endswith("/oidc/userinfo")
PY

remote_ui_status="$(curl_status "rmcryptpad.localhost" "https://rmcryptpad.localhost:${PORT}/ui/cryptpad/remoteEntry.js")"
log "GET https://rmcryptpad.localhost:${PORT}/ui/cryptpad/remoteEntry.js -> ${remote_ui_status}"

USER_KEY="${TMP_DIR}/tim.key"
USER_CERT="${TMP_DIR}/tim.crt"
openssl req \
  -x509 \
  -newkey rsa:2048 \
  -sha256 \
  -nodes \
  -days 2 \
  -subj '/CN=tim' \
  -keyout "${USER_KEY}" \
  -out "${USER_CERT}" \
  >/dev/null 2>&1

USER_FINGERPRINT="$(openssl x509 -in "${USER_CERT}" -noout -fingerprint | cut -d= -f2)"
USER_PAYLOAD="$(python3 - "${USER_CERT}" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as handle:
    cert = handle.read()

print(json.dumps({
    "uuid": "uuid-tim",
    "callsign": "tim",
    "x509cert": cert,
}))
PY
)"

curl_body \
  "rmcryptpad.localhost" \
  "https://rmcryptpad.localhost:${PORT}/api/v1/users/created" \
  -X POST \
  -H 'Content-Type: application/json' \
  -H 'X-ClientCert-DN: CN=rasenmaeher,O=RM' \
  -H 'X-SSL-Client-Verify: SUCCESS' \
  --data "${USER_PAYLOAD}" \
  >/dev/null

user_create_status="$(
  curl_status \
    "rmcryptpad.localhost" \
    "https://rmcryptpad.localhost:${PORT}/api/v1/users/created" \
    -X POST \
    -H 'Content-Type: application/json' \
    -H 'X-ClientCert-DN: CN=rasenmaeher,O=RM' \
    -H 'X-SSL-Client-Verify: SUCCESS' \
    --data "${USER_PAYLOAD}"
)"
log "POST https://rmcryptpad.localhost:${PORT}/api/v1/users/created -> ${user_create_status}"

CODE_VERIFIER='correct-horse-battery-staple'
CODE_CHALLENGE="$(python3 - <<'PY'
import base64
import hashlib

value = b"correct-horse-battery-staple"
print(base64.urlsafe_b64encode(hashlib.sha256(value).digest()).decode("utf-8").rstrip("="))
PY
)"
REDIRECT_URI="https://cryptpad.localhost:${PORT}/ssoauth/"
AUTHZ_HEADERS="${TMP_DIR}/authz.headers"

curl -sS \
  --cacert "${TLS_CERT}" \
  --resolve "rmcryptpad.localhost:${PORT}:127.0.0.1" \
  -D "${AUTHZ_HEADERS}" \
  -o /dev/null \
  -H 'X-ClientCert-DN: CN=tim,O=RM' \
  -H 'X-SSL-Client-Verify: SUCCESS' \
  -H "X-SSL-Client-Fingerprint: ${USER_FINGERPRINT}" \
  --get \
  --data-urlencode 'client_id=cryptpad' \
  --data-urlencode "redirect_uri=${REDIRECT_URI}" \
  --data-urlencode 'response_type=code' \
  --data-urlencode 'scope=openid profile' \
  --data-urlencode "code_challenge=${CODE_CHALLENGE}" \
  --data-urlencode 'code_challenge_method=S256' \
  --data-urlencode 'nonce=nonce-smoke' \
  --data-urlencode 'state=state-smoke' \
  "https://rmcryptpad.localhost:${PORT}/oidc/authorize"

AUTHZ_STATUS="$(awk 'NR==1 {print $2}' "${AUTHZ_HEADERS}" | tr -d '\r')"
[ "${AUTHZ_STATUS}" = '302' ]
log "GET https://rmcryptpad.localhost:${PORT}/oidc/authorize -> ${AUTHZ_STATUS}"

LOCATION="$(awk 'BEGIN {IGNORECASE=1} /^Location:/ {print $2}' "${AUTHZ_HEADERS}" | tr -d '\r')"
log "OIDC authorize redirect location: ${LOCATION}"
AUTHZ_CODE="$(python3 - "${LOCATION}" <<'PY'
import sys
import urllib.parse

location = sys.argv[1]
parsed = urllib.parse.urlparse(location)
params = urllib.parse.parse_qs(parsed.query)
assert params["state"] == ["state-smoke"]
print(params["code"][0])
PY
)"
log "OIDC authorize code: $(redact_token "${AUTHZ_CODE}")"

TOKEN_JSON="$(
  curl_body \
    "rmcryptpad.localhost" \
    "https://rmcryptpad.localhost:${PORT}/oidc/token" \
    -X POST \
    -u 'cryptpad:change-me' \
    -H 'Content-Type: application/x-www-form-urlencoded' \
    --data-urlencode 'grant_type=authorization_code' \
    --data-urlencode "code=${AUTHZ_CODE}" \
    --data-urlencode "redirect_uri=${REDIRECT_URI}" \
    --data-urlencode "code_verifier=${CODE_VERIFIER}"
)"
log "POST https://rmcryptpad.localhost:${PORT}/oidc/token -> 200"
log "Token response summary:"
python3 - "${TOKEN_JSON}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
print(
    json.dumps(
        {
            "token_type": payload["token_type"],
            "scope": payload["scope"],
            "access_token": f'{payload["access_token"][:8]}...{payload["access_token"][-8:]} (len={len(payload["access_token"])})',
            "id_token": f'present (len={len(payload["id_token"])})',
        },
        indent=2,
        sort_keys=True,
    )
)
PY

ACCESS_TOKEN="$(python3 - "${TOKEN_JSON}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["token_type"] == "Bearer"
assert payload["scope"] == "openid profile"
assert payload["id_token"]
print(payload["access_token"])
PY
)"

USERINFO_JSON="$(
  curl_body \
    "rmcryptpad.localhost" \
    "https://rmcryptpad.localhost:${PORT}/oidc/userinfo" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}"
)"
log "GET https://rmcryptpad.localhost:${PORT}/oidc/userinfo -> 200"
log "Userinfo selected claims:"
python3 - "${USERINFO_JSON}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
print(
    json.dumps(
        {
            "sub": payload["sub"],
            "preferred_username": payload["preferred_username"],
            "name": payload["name"],
        },
        indent=2,
        sort_keys=True,
    )
)
PY

python3 - "${USERINFO_JSON}" <<'PY'
import json
import sys

payload = json.loads(sys.argv[1])
assert payload["sub"] == "tim"
assert payload["preferred_username"] == "tim"
assert payload["name"] == "tim"
PY
