#!/bin/bash
# update.sh — Pull latest images and restart the RASENMAEHER stack.
# Run from the deploy directory.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'; BOLD='\033[1m'; NC='\033[0m'
ok()   { echo -e "${GREEN}[✓]${NC} $*"; }
info() { echo -e "${CYAN}[*]${NC} $*"; }
err()  { echo -e "${RED}[✗]${NC} $*"; exit 1; }

[ -f "$ENV_FILE" ] || err ".env not found — run ./install.sh first"

cd "$SCRIPT_DIR"

info "Pulling latest images..."
docker compose pull --quiet
ok "Images pulled"

info "Rebuilding TAK server..."
docker compose build --quiet takserver
ok "TAK server rebuilt"

info "Restarting stack..."
docker compose up -d --remove-orphans
ok "Stack restarted"

echo ""
echo -e "  ${BOLD}Done.${NC}  Logs: docker compose logs -f"
