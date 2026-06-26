#!/bin/bash
# update.sh — Pull latest and restart the RASENMAEHER stack.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${CYAN}[*]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }

[ -f "$ENV_FILE" ] || err ".env not found — run ./install.sh first"

# Detect which compose file was used
if docker compose -p rmlocal ps --quiet 2>/dev/null | grep -q .; then
    COMPOSE="docker compose -p rmlocal -f docker-compose-local.yml"
    DOCKER_REPO_PREFIX="localhost:5050/"
    LOCAL_MODE=true
else
    COMPOSE="docker compose -f docker-compose.yml"
    DOCKER_REPO_PREFIX=""
    LOCAL_MODE=false
fi

cd "$SCRIPT_DIR"

if $LOCAL_MODE; then
    info "Rebuilding all images (local mode)..."
    PVARKI_DOCKER_REPO="$DOCKER_REPO_PREFIX" $COMPOSE build --pull --quiet
    ok "Images rebuilt"
    info "Restarting stack..."
    PVARKI_DOCKER_REPO="$DOCKER_REPO_PREFIX" $COMPOSE up -d --remove-orphans
else
    info "Pulling latest images..."
    $COMPOSE pull --quiet
    ok "Images pulled"
    info "Rebuilding TAK server..."
    $COMPOSE build --quiet takserver
    ok "TAK server rebuilt"
    info "Restarting stack..."
    $COMPOSE up -d --remove-orphans
fi

ok "Stack restarted"
echo ""
echo -e "  ${BOLD}Done.${NC}  Logs: $COMPOSE logs -f"
