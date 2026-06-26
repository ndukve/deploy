#!/usr/bin/env bash
set -e

# Load profile to restore PATH, pnpm, uv env, etc.
export PATH=/root/.local/bin:/ui/node_modules/.bin:$PATH

echo "Installing dev dependencies..."
pnpm --dir /ui install

/app/docker/container-init.sh

uv sync --frozen

mkdir -p /ui_files/mtx

echo "Starting pnpm build --watch..."
pnpm --dir /ui build --outDir /ui_files/mtx --watch &

echo "Starting uvicorn..."
uv run uvicorn --host 0.0.0.0 --port 8005 --log-level debug \
    --factory rmmtxauthz.web.application:get_app --reload
