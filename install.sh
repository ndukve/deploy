#!/bin/bash
# install.sh — RASENMAEHER Deploy App installer
# Can be run directly or via:
#   curl -fsSL https://raw.githubusercontent.com/ndukve/deploy/main/install.sh | bash

set -euo pipefail

REPO_URL="https://github.com/ndukve/deploy.git"  # update to your fork if needed
INSTALL_DIR="${INSTALL_DIR:-$HOME/deploy}"

# ── Bootstrap: clone repo if running via curl | bash ──────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" 2>/dev/null && pwd || echo "$PWD")"
if [ ! -f "$SCRIPT_DIR/docker-compose.yml" ]; then
    echo "Bootstrapping — cloning repo to $INSTALL_DIR ..."
    if ! command -v git &>/dev/null; then
        apt-get update -qq && apt-get install -y -qq git
    fi
    if [ -d "$INSTALL_DIR/.git" ]; then
        git -C "$INSTALL_DIR" pull --ff-only
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi
    exec bash "$INSTALL_DIR/install.sh" < /dev/tty
fi

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

# ── Environment ───────────────────────────────────────────────────────────────
section "Installation type"
echo ""
echo -e "  ${BOLD}1) Local / test VM${NC}"
echo "     No domain or public IP needed."
echo "     Uses localmaeher.dev.pvarki.fi (public DNS → 127.0.0.1) + mkcert certs."
echo "     Access: https://localmaeher.dev.pvarki.fi:4439"
echo "     Requirements:"
echo "       ✓  VM on any network (local, LAN, cloud)"
echo "       ✓  16 GB RAM, 8 CPU cores, 60 GB disk"
echo "       ✗  No domain, DNS, or open ports needed"
echo ""
echo -e "  ${BOLD}2) Production${NC}"
echo "     Real domain, public IP, Let's Encrypt certs."
echo "     Requirements:"
echo "       ✓  Public IP on this VM"
echo "       ✓  Domain name with Cloudflare wildcard DNS → this IP (grey-cloud)"
echo "       ✓  Email address for Let's Encrypt"
echo "       ✓  Ports open: 80, 443, 4626, 4627, 8089, 8443, 9443"
echo "       ✓  32 GB RAM recommended"
echo ""
read -rp "$(echo -e "  ${BOLD}Which applies to you? [1/2]:${NC} ")" _ENV_CHOICE

LOCAL_MODE=false
COMPOSE_FILE="docker-compose.yml"
COMPOSE_PROJECT=""

if [[ "${_ENV_CHOICE:-1}" == "1" ]]; then
    LOCAL_MODE=true
    COMPOSE_FILE="docker-compose-local.yml"
    COMPOSE_PROJECT="-p rmlocal"
    SERVER_DOMAIN="localmaeher.dev.pvarki.fi"
    MW_LE_EMAIL="test@example.com"
    MW_LE_TEST="true"
    MW_MKCERT="true"
    CFSSL_CA_NAME="localmaeher"
    ok "Local mode — using $SERVER_DOMAIN"
    echo ""
    echo "  Access after install:"
    echo "    https://localmaeher.dev.pvarki.fi:4439"
else
    LOCAL_MODE=false
    section "Domain"
    echo "  DNS records required (all → this VM's public IP):"
    echo "    yourdomain.com, *.yourdomain.com  (Cloudflare wildcard, grey-cloud)"
    echo ""
    ask SERVER_DOMAIN "Server domain (e.g. example.com)" ""
    ask MW_LE_EMAIL   "Email for Let's Encrypt" ""
    ask MW_LE_TEST    "Use staging certs? (true while testing, false for real certs)" "true"
    MW_MKCERT="false"

    section "Certificate Authority"
    ask CFSSL_CA_NAME "Internal CA name" "${SERVER_DOMAIN%%.*}-ca"
fi

# ── Generate secrets ──────────────────────────────────────────────────────────
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
if $LOCAL_MODE; then
    echo "  Mode            : Local test VM"
    echo "  Compose file    : $COMPOSE_FILE"
else
    echo "  Mode            : Production"
fi
echo "  Domain          : $SERVER_DOMAIN"
echo "  Passwords       : (auto-generated, saved to .env)"
echo ""
read -rp "$(echo -e "  ${BOLD}Proceed?${NC} [Y/n]: ")" _CONFIRM
[[ "${_CONFIRM:-Y}" =~ ^[Yy] ]] || { echo "Aborted."; exit 0; }

# ── Fix DNS if needed ─────────────────────────────────────────────────────────
if ! getent hosts debian.org > /dev/null 2>&1; then
    warn "DNS not resolving — adding fallback 1.1.1.1"
    echo "nameserver 1.1.1.1" >> /etc/resolv.conf
fi

# ── Install Docker ────────────────────────────────────────────────────────────
if ! command -v docker &>/dev/null; then
    start_timer "Installing Docker..."
    curl -fsSL https://get.docker.com | sh > /dev/null 2>&1
    systemctl enable --now docker > /dev/null 2>&1
    stop_timer; ok "Docker installed"
else
    ok "Docker $(docker --version | awk '{print $3}' | tr -d ,) present"
fi

[ -n "${SUDO_USER:-}" ] && { usermod -aG docker "$SUDO_USER"; ok "Added $SUDO_USER to docker group"; }

# ── Write .env ────────────────────────────────────────────────────────────────
info "Writing .env..."
cat > "$ENV_FILE" << ENVEOF
# RASENMAEHER .env — generated by install.sh on $(date -u '+%Y-%m-%d %H:%M UTC')
# DO NOT commit to version control.

SERVER_DOMAIN=${SERVER_DOMAIN}
CFSSL_CA_NAME=${CFSSL_CA_NAME}
MW_LE_EMAIL=${MW_LE_EMAIL}
MW_LE_TEST=${MW_LE_TEST}
MW_MKCERT=${MW_MKCERT}
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

# ── Local mode: start registry ─────────────────────────────────────────────────
DOCKER_REPO_PREFIX=""
if $LOCAL_MODE; then
    if ! docker ps --filter "name=registry" --filter "status=running" --format "{{.Names}}" | grep -q "^registry$"; then
        info "Starting local image registry..."
        docker run -d -p 5050:5000 --restart always --name registry registry:3 > /dev/null
        ok "Local registry running on :5050"
    else
        ok "Local registry already running"
    fi
    DOCKER_REPO_PREFIX="localhost:5050/"
fi

# ── Build & start ─────────────────────────────────────────────────────────────
cd "$SCRIPT_DIR"

COMPOSE="docker compose $COMPOSE_PROJECT -f $COMPOSE_FILE"

if $LOCAL_MODE; then
    # takrmapi builds FROM the takserver image — build and push it to the local
    # registry first so it's available when the parallel build starts.
    start_timer "Building TAK server image (base for takrmapi)..."
    PVARKI_DOCKER_REPO="$DOCKER_REPO_PREFIX" $COMPOSE build --pull --push --quiet takserver
    stop_timer; ok "TAK server built and pushed to local registry"

    start_timer "Building all images (local mode — first build takes 10-20 min)..."
    PVARKI_DOCKER_REPO="$DOCKER_REPO_PREFIX" $COMPOSE build --quiet
    stop_timer; ok "Images built"
else
    start_timer "Pulling pre-built images from ghcr.io..."
    $COMPOSE pull --quiet 2>/dev/null || true
    stop_timer; ok "Images pulled"

    start_timer "Building TAK server from local Dockerfile..."
    $COMPOSE build --quiet takserver
    stop_timer; ok "TAK server image built"
fi

start_timer "Starting stack (first boot: 5-15 min)..."
if $LOCAL_MODE; then
    PVARKI_DOCKER_REPO="$DOCKER_REPO_PREFIX" $COMPOSE up -d
else
    $COMPOSE up -d
fi
stop_timer; ok "Stack started"

# ── Wait for rmapi ─────────────────────────────────────────────────────────────
info "Waiting for rmapi to be healthy..."
TIMEOUT=900
ELAPSED=0
while ! $COMPOSE exec -T rmapi rasenmaeher_api healthcheck > /dev/null 2>&1; do
    sleep 10
    ELAPSED=$(( ELAPSED + 10 ))
    if [ $ELAPSED -ge $TIMEOUT ]; then
        warn "rmapi not healthy after ${TIMEOUT}s"
        warn "Check logs: $COMPOSE logs rmapi"
        break
    fi
done
ok "rmapi healthy"

# ── First admin code ───────────────────────────────────────────────────────────
echo ""
ADMIN_CODE=$($COMPOSE exec -T rmapi /bin/bash -c "rasenmaeher_api addcode" 2>/dev/null \
    || echo "(run manually: $COMPOSE exec rmapi rasenmaeher_api addcode)")

if $LOCAL_MODE; then
    LOGIN_URL="https://localmaeher.dev.pvarki.fi:4439"
    HOME_URL="https://mtls.localmaeher.dev.pvarki.fi:4439"
    KC_URL="https://kc.localmaeher.dev.pvarki.fi:9443/admin/RASENMAEHER/console/"
    TAK_URL="https://tak.localmaeher.dev.pvarki.fi:8443/"
else
    LOGIN_URL="https://${SERVER_DOMAIN}"
    HOME_URL="https://mtls.${SERVER_DOMAIN}"
    KC_URL="https://kc.${SERVER_DOMAIN}:9443/admin/RASENMAEHER/console/"
    TAK_URL="https://tak.${SERVER_DOMAIN}:8443/"
fi

echo -e "${BOLD}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}${BOLD}║              RASENMAEHER is up!                              ║${NC}"
echo -e "${BOLD}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Login page     : ${BOLD}${LOGIN_URL}${NC}"
echo -e "  Home (mTLS)    : ${BOLD}${HOME_URL}${NC}"
echo -e "  Keycloak admin : ${BOLD}${KC_URL}${NC}"
echo -e "  TAK admin      : ${BOLD}${TAK_URL}${NC}"
echo ""
echo -e "  First admin code: ${BOLD}${ADMIN_CODE}${NC}"
echo ""
echo "  Secrets saved to : $ENV_FILE"
echo "  View logs        : $COMPOSE logs -f"
echo "  Update           : ./update.sh"
echo ""
