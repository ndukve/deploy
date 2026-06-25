#!/bin/bash
# install.sh — RASENMAEHER Deploy App installer
# Installs the full stack: TAK, Keycloak, Matrix, Battlelog, CryptPad, MediaMTX
# Run as root on a fresh VM.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "$PWD")"
ENV_FILE="$SCRIPT_DIR/.env"

[ -t 0 ] || exec < /dev/tty 2>/dev/null || true

if [[ $EUID -ne 0 ]]; then
    echo "Root required — re-running with sudo..."
    exec sudo bash "$SCRIPT_DIR/install.sh"
fi

# ── Colours ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()      { echo -e "${GREEN}[✓]${NC} $*"; }
info()    { echo -e "${CYAN}[*]${NC} $*"; }
warn()    { echo -e "${YELLOW}[!]${NC} $*"; }
err()     { echo -e "${RED}[✗]${NC} $*"; exit 1; }
section() { echo -e "\n${CYAN}── $* ──────────────────────────────────────────────────────${NC}"; }

ask() {
    local _var="$1" _q="$2" _default="${3:-}" _ans
    if [ -n "$_default" ]; then
        read -rp "$(echo -e "  ${BOLD}${_q}${NC} [${_default}]: ")" _ans
        printf -v "$_var" '%s' "${_ans:-$_default}"
    else
        while true; do
            read -rp "$(echo -e "  ${BOLD}${_q}${NC}: ")" _ans
            [ -n "$_ans" ] && break
            echo "    (required)"
        done
        printf -v "$_var" '%s' "$_ans"
    fi
}

ask_secret() {
    local _var="$1" _q="$2" _ans
    while true; do
        read -rsp "$(echo -e "  ${BOLD}${_q}${NC}: ")" _ans; echo
        [ -n "$_ans" ] && break
        echo "    (required)"
    done
    printf -v "$_var" '%s' "$_ans"
}

gen_pass()   { openssl rand -hex 20; }
gen_uuid()   { python3 -c 'import uuid; print(uuid.uuid4())'; }
gen_secret() { openssl rand -base64 32 | tr -d '=/+' | head -c 32; }

# ── Timer ─────────────────────────────────────────────────────────────────────
_timer_pid=""
start_timer() {
    local label="$1" start cols
    start=$(date +%s); cols=$(tput cols 2>/dev/null || echo 80)
    ( while true; do
        local e mm ss
        e=$(( $(date +%s) - start )); mm=$(( e/60 )); ss=$(( e%60 ))
        printf "\r  ${CYAN}[*]${NC} %-$(( cols - 14 ))s ${BOLD}%02d:%02d${NC}" "$label" "$mm" "$ss"
        sleep 1
    done ) &
    _timer_pid=$!
}
stop_timer() {
    [ -n "$_timer_pid" ] && { kill "$_timer_pid" 2>/dev/null; wait "$_timer_pid" 2>/dev/null || true; _timer_pid=""; }
    printf "\r\033[K"
}
trap '[ -n "$_timer_pid" ] && kill "$_timer_pid" 2>/dev/null' EXIT

# ── Banner ────────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}  RASENMAEHER — Deploy App Installer${NC}"
echo "  Full stack: TAK · Keycloak · Matrix · Battlelog · CryptPad · MediaMTX"
echo ""

# ── DNS / domain ─────────────────────────────────────────────────────────────
section "Domain"
echo "  Required DNS records (all → this VM's public IP):"
echo "    domain, kc.domain, tak.domain, bl.domain, mtx.domain,"
echo "    matrix.domain, synapse.domain, cryptpad.domain,"
echo "    sandbox.cryptpad.domain, rmcryptpad.domain,"
echo "    mtls.* for all of the above"
echo ""
ask SERVER_DOMAIN "Server domain (e.g. example.com)" ""
ask MW_LE_EMAIL   "Email for Let's Encrypt" ""
ask MW_LE_TEST    "Let's Encrypt test mode (true=staging certs, false=real certs)" "true"

# ── CA / cert settings ────────────────────────────────────────────────────────
section "Certificate Authority"
ask CFSSL_CA_NAME "Internal CA name" "${SERVER_DOMAIN%%.*}-ca"

# ── Passwords (auto-generated, shown at end) ──────────────────────────────────
section "Secrets"
info "Generating all passwords and secrets..."

KEYCLOAK_DATABASE_PASSWORD=$(gen_pass)
RM_DATABASE_PASSWORD=$(gen_pass)
POSTGRES_PASSWORD=$(gen_pass)
LDAP_ADMIN_PASSWORD=$(gen_pass)
KEYCLOAK_ADMIN_PASSWORD=$(gen_pass)
TAK_DATABASE_PASSWORD=$(gen_pass)
SYNAPSE_DATABASE_PASSWORD=$(gen_pass)
SYNAPSE_MACAROON_SECRET_KEY=$(gen_secret)
SYNAPSE_REGISTRATION_SECRET=$(gen_secret)
TAKSERVER_CERT_PASS=$(gen_pass)
TAK_CA_PASS=$(gen_pass)
KEYCLOAK_PROFILEROOT_UUID=$(gen_uuid)
KEYCLOAK_HTTPS_KEY_STORE_PASSWORD=$(gen_pass)
KEYCLOAK_HTTPS_TRUST_STORE_PASSWORD=$(gen_pass)
BL_DATABASE_PASSWORD=$(gen_pass)
RMMTX_DATABASE_PASSWORD=$(gen_pass)
RMMTX_API_PASSWORD=$(gen_pass)
RMMTX_SRT_PUB_PASSWORD=$(gen_pass)
RMMTX_SRT_READ_PASSWORD=$(gen_pass)
RMCRYPTPAD_DATABASE_PASSWORD=$(gen_pass)
RMCRYPTPAD_OIDC_CLIENT_SECRET=$(gen_secret)
VITE_THEME="default"

ok "Secrets generated"

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}── Summary ──────────────────────────────────────────────────────────${NC}"
echo "  Domain          : $SERVER_DOMAIN"
echo "  LE email        : $MW_LE_EMAIL"
echo "  LE test mode    : $MW_LE_TEST"
echo "  CA name         : $CFSSL_CA_NAME"
echo "  Passwords       : (auto-generated, saved to .env)"
echo ""
read -rp "$(echo -e "  ${BOLD}Proceed?${NC} [Y/n]: ")" _CONFIRM
[[ "${_CONFIRM:-Y}" =~ ^[Yy] ]] || { echo "Aborted."; exit 0; }

# ── DNS check ──────────────────────────────────────────────────────────────────
if ! getent hosts debian.org > /dev/null 2>&1; then
    warn "DNS not resolving — adding fallback 1.1.1.1"
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf
fi

# ── Docker ────────────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    start_timer "Installing Docker..."
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl enable --now docker > /dev/null 2>&1
    stop_timer; ok "Docker installed"
else
    ok "Docker $(docker --version | awk '{print $3}' | tr -d ,) present"
fi

[ -n "${SUDO_USER:-}" ] && { usermod -aG docker "$SUDO_USER"; ok "Added $SUDO_USER to docker group"; }

# ── Write .env ─────────────────────────────────────────────────────────────────
info "Writing .env..."
cat > "$ENV_FILE" << ENVEOF
# RASENMAEHER .env — generated by install.sh on $(date -u '+%Y-%m-%d %H:%M UTC')
# DO NOT commit to version control.

SERVER_DOMAIN=${SERVER_DOMAIN}
CFSSL_CA_NAME=${CFSSL_CA_NAME}
MW_LE_EMAIL=${MW_LE_EMAIL}
MW_LE_TEST=${MW_LE_TEST}
VITE_THEME=${VITE_THEME}

KEYCLOAK_DATABASE_PASSWORD=${KEYCLOAK_DATABASE_PASSWORD}
RM_DATABASE_PASSWORD=${RM_DATABASE_PASSWORD}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
LDAP_ADMIN_PASSWORD=${LDAP_ADMIN_PASSWORD}
KEYCLOAK_ADMIN_PASSWORD=${KEYCLOAK_ADMIN_PASSWORD}
TAK_DATABASE_PASSWORD=${TAK_DATABASE_PASSWORD}
SYNAPSE_DATABASE_PASSWORD=${SYNAPSE_DATABASE_PASSWORD}
SYNAPSE_MACAROON_SECRET_KEY=${SYNAPSE_MACAROON_SECRET_KEY}
SYNAPSE_REGISTRATION_SECRET=${SYNAPSE_REGISTRATION_SECRET}
TAKSERVER_CERT_PASS=${TAKSERVER_CERT_PASS}
TAK_CA_PASS=${TAK_CA_PASS}
KEYCLOAK_PROFILEROOT_UUID=${KEYCLOAK_PROFILEROOT_UUID}
KEYCLOAK_HTTPS_KEY_STORE_PASSWORD=${KEYCLOAK_HTTPS_KEY_STORE_PASSWORD}
KEYCLOAK_HTTPS_TRUST_STORE_PASSWORD=${KEYCLOAK_HTTPS_TRUST_STORE_PASSWORD}
BL_DATABASE_PASSWORD=${BL_DATABASE_PASSWORD}
RMMTX_DATABASE_PASSWORD=${RMMTX_DATABASE_PASSWORD}
RMMTX_API_PASSWORD=${RMMTX_API_PASSWORD}
RMMTX_SRT_PUB_PASSWORD=${RMMTX_SRT_PUB_PASSWORD}
RMMTX_SRT_READ_PASSWORD=${RMMTX_SRT_READ_PASSWORD}
RMCRYPTPAD_DATABASE_PASSWORD=${RMCRYPTPAD_DATABASE_PASSWORD}
RMCRYPTPAD_OIDC_CLIENT_SECRET=${RMCRYPTPAD_OIDC_CLIENT_SECRET}
ENVEOF
chmod 600 "$ENV_FILE"
ok ".env written (mode 600)"

# ── Build & start ─────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"

start_timer "Pulling pre-built images from ghcr.io..."
docker compose pull --quiet 2>/dev/null || true
stop_timer; ok "Images pulled"

start_timer "Building TAK server from local Dockerfile (custom scripts)..."
docker compose build --quiet takserver
stop_timer; ok "TAK server image built"

start_timer "Starting stack (this takes 5-10 min on first boot)..."
docker compose up -d
stop_timer; ok "Stack started"

# ── Wait for rmapi ─────────────────────────────────────────────────────────────
info "Waiting for rmapi to be healthy..."
TIMEOUT=600
ELAPSED=0
while ! docker compose exec -T rmapi rasenmaeher_api healthcheck > /dev/null 2>&1; do
    sleep 10
    ELAPSED=$(( ELAPSED + 10 ))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        warn "rmapi not healthy after ${TIMEOUT}s — check logs: docker compose logs rmapi"
        break
    fi
done
ok "rmapi healthy"

# ── First admin code ───────────────────────────────────────────────────────────
echo ""
ADMIN_CODE=$(docker compose exec -T rmapi /bin/bash -c "rasenmaeher_api addcode" 2>/dev/null || echo "(run manually: docker compose exec rmapi rasenmaeher_api addcode)")

echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║              RASENMAEHER is up!                              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Login page     : ${BOLD}https://${SERVER_DOMAIN}${NC}"
echo -e "  Home (mTLS)    : ${BOLD}https://mtls.${SERVER_DOMAIN}${NC}"
echo -e "  Keycloak admin : ${BOLD}https://kc.${SERVER_DOMAIN}:9443/admin/RASENMAEHER/console/${NC}"
echo -e "  TAK admin      : ${BOLD}https://tak.${SERVER_DOMAIN}:8443/${NC}"
echo ""
echo -e "  First admin code: ${BOLD}${ADMIN_CODE}${NC}"
echo ""
echo "  Secrets saved to: $ENV_FILE"
echo "  View logs       : docker compose logs -f"
echo "  Update          : ./update.sh"
echo ""
