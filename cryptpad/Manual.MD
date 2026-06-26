# CryptPad Local Setup Manual

## Goal

Build a fully local CryptPad deployment that follows the official two-origin installation model closely enough to validate it before we fold it into a larger Docker Compose stack.

## Installation

```bash
printf 'CPAD_UID=%s\nCPAD_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
docker compose ps
docker compose logs --no-color cryptpad
```

## Fixed Decisions

- Local mode uses `https://cryptpad.localhost:8443` as the main origin.
- Local mode uses `https://sandbox.cryptpad.localhost:8443` as the sandbox origin.
- Nginx terminates TLS and proxies both HTTP traffic and `/cryptpad_websocket`.
- CryptPad runs in Docker with persistent bind-mounted data directories.
- `rmcryptpad` runs in Docker with PostgreSQL-backed state and a local OIDC signing-key volume.
- Local TLS uses a self-signed certificate generated automatically on first start.

## Current Status

- [x] Read the official install documentation and upstream Docker/Nginx examples.
- [x] Choose the local-domain strategy.
- [x] Write the design note and implementation plan.
- [x] Create the Docker Compose stack.
- [x] Build and boot the stack.
- [x] Verify HTTPS, proxying, and CryptPad startup.
- [x] Capture the onboarding and operator workflow.
- [x] Approve the Rasenmaeher integration architecture.
- [x] Write the Rasenmaeher integration implementation plan.
- [x] Implement the Rasenmaeher integration sidecar, SSO flow, and product UI.
- [x] Wire the local Compose stack to `postgres`, `rmcryptpad`, and the CryptPad SSO plugin.
- [x] Wire this repository into the outer `docker-rasenmaeher-integration` stack for full mTLS browser verification.

## Working Rules

- Keep this file updated whenever the setup, commands, or verification status changes.
- Keep the stack aligned with the official install guidance where practical.
- Favor pinned slim images, non-root runtime where possible, and internal-only service exposure.
- Keep CryptPad implementation and future integration work in this repository, not in the `docker-rasenmaeher-integration` repository.

## Repository Status

- Source repository: `git@github.com:pvarki/cryptpad.git`
- Current local-stack baseline is published on branch `main`.

## Planned File Layout

- `compose.yaml`
- `config/config.js`
- `config/sso.js`
- `customize/application_config.js`
- `docker/cryptpad/`
- `docker/nginx/`
- `docker/scripts/`
- `rmcryptpad/`
- `volumes/`

## Expected Local Workflow

1. Run `docker compose up -d --build`.
2. Open `https://cryptpad.localhost:8443`.
3. Accept the local certificate warning.
4. Check `docker compose logs cryptpad` for the onboarding URL.
5. Verify `https://rmcryptpad.localhost:8443/.well-known/openid-configuration`.
6. Visit `https://cryptpad.localhost:8443/checkup/` after startup.

## Verified State

- `docker compose config` passes.
- `docker compose up -d --build` succeeds.
- `docker compose ps` shows `postgres`, `rmcryptpad`, and `cryptpad` healthy, with `nginx` running.
- `curl -kI https://cryptpad.localhost:8443` returns `HTTP/2 200`.
- `curl -kI https://sandbox.cryptpad.localhost:8443` returns `HTTP/2 200`.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443` succeeds.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://sandbox.cryptpad.localhost:8443` succeeds.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem https://rmcryptpad.localhost:8443/.well-known/openid-configuration` returns `HTTP/2 200`.
- `curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://rmcryptpad.localhost:8443/ui/cryptpad/remoteEntry.js` returns `HTTP/2 200`.
- The generated certificate contains both SANs:
  - `DNS:cryptpad.localhost`
  - `DNS:sandbox.cryptpad.localhost`
  - `DNS:rmcryptpad.localhost`
- `curl -kI https://cryptpad.localhost:8443/checkup/` returns `HTTP/2 200`.

## Onboarding URL

Fetch the current install URL for the active data set with:

```bash
docker compose logs cryptpad
```

## Known Local Notes

- The stack uses a self-signed certificate generated automatically into `volumes/nginx/certs/`.
- If you are upgrading an older checkout from the earlier two-host local stack, delete `volumes/nginx/certs/cryptpad.local.pem` and `volumes/nginx/certs/cryptpad.local-key.pem` once before restarting so the regenerated cert includes `rmcryptpad.localhost`.
- Browsers will warn about the certificate until you accept it or trust the local cert manually.
- With the self-signed local setup, you may need to open both `https://cryptpad.localhost:8443` and `https://sandbox.cryptpad.localhost:8443` directly once so the browser accepts the certificate on both origins before signup and editor flows work reliably.
- The local setup records your host UID/GID in `.env` and runs the CryptPad container with that identity so the bind-mounted data stays host-accessible.
- The local setup also runs `postgres` and `rmcryptpad` with that identity so the sidecar OIDC key material and Postgres data stay in bind mounts under `volumes/`.
- The stack publishes only `8443` on the host. Internal CryptPad ports `3000` and `3003` stay on the Docker network.
- The curl commands in `Verified State` are optional smoke checks, not required installation steps.
- Repo-local verification proves product services and wiring. Full browser mTLS validation belongs to the local-only integration branch in `/home/elderx/dev/docker-rasenmaeher-integration`.
- Rasenmaeher sends `x509cert` using the existing CFSSL-style escaped-newline contract, so `rmcryptpad` must normalize `\\n` back to PEM before fingerprinting and storing the user cert.
- In the integrated stack, CryptPad's server-side OIDC discovery must use the internal `rmcryptpad` service URL, while the discovery document still advertises the public `rmcryptpad.${SERVER_DOMAIN}` issuer for browser redirects.
- In the integrated stack, CryptPad's server-side OIDC callback exchange hits the public `rmcryptpad.${SERVER_DOMAIN}` HTTPS endpoints, so the CryptPad container must trust the stack TLS roots from both `/ca_public/miniwerk_ca.pem` and `/ca_public/ca_chain.pem`.

## Troubleshooting

- If signup succeeds and then a white page appears, open `https://sandbox.cryptpad.localhost:8443/` directly, accept the certificate there too, then refresh the main site.
- If rich text shows browser-console errors but the server logs show `200` for `/pad/ckeditor-inner.html`, `/common/testworker.js`, and `/common/worker.bundle.min.js`, test again in a clean browser profile or incognito window with extensions disabled.
- `contentInt.js` console messages are not part of the CryptPad codebase in this setup and likely come from a browser extension.
- In the integrated Rasenmaeher stack, the product card must open CryptPad at `/login/`, not `/`, so CryptPad starts the enforced SSO flow instead of dropping the user into guest mode.

## Next Step

Continue refining the local-only `cryptpad-development` branch in `/home/elderx/dev/docker-rasenmaeher-integration` as the integration baseline for the larger stack.
