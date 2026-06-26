# Local CryptPad

This project brings up a fully local CryptPad stack with Docker Compose using the recommended two-origin model and an `rmcryptpad` sidecar for the Deploy App / Rasenmaeher integration flow:

- `https://cryptpad.localhost:8443`
- `https://sandbox.cryptpad.localhost:8443`
- `https://rmcryptpad.localhost:8443`

The local stack includes:

- upstream CryptPad
- official CryptPad SSO plugin configured for `rmcryptpad`
- `rmcryptpad` FastAPI sidecar with PostgreSQL persistence
- Nginx for HTTPS, websocket proxying, and local host routing

The stack generates a self-signed local certificate on first boot.

If you are upgrading an older local checkout from the earlier two-host setup, delete `volumes/nginx/certs/cryptpad.local.pem` and `volumes/nginx/certs/cryptpad.local-key.pem` once before restarting so the regenerated cert includes `rmcryptpad.localhost`.

## Start

```bash
printf 'CPAD_UID=%s\nCPAD_GID=%s\n' "$(id -u)" "$(id -g)" > .env
docker compose up -d --build
```

Check the running services:

```bash
docker compose ps
```

## Open

```text
https://cryptpad.localhost:8443
https://sandbox.cryptpad.localhost:8443
https://rmcryptpad.localhost:8443
```

Your browser will warn about the local self-signed certificate. Accept the warning to continue local testing.

If you want command-line certificate validation without `-k`, use the generated local cert:

```bash
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://sandbox.cryptpad.localhost:8443
curl --cacert volumes/nginx/certs/cryptpad.local.pem https://rmcryptpad.localhost:8443/.well-known/openid-configuration
```

## First-run checks

Get the onboarding URL from the CryptPad logs:

```bash
docker compose logs cryptpad
```

After the instance is up, run the diagnostics page:

```text
https://cryptpad.localhost:8443/checkup/
```

## Operator notes

The living setup runbook is in `Manual.MD`.

Repo-local verification covers the product services, SSO image wiring, OIDC discovery, UI asset delivery, and the local Docker Compose runtime.

Full browser mTLS login, Deploy App product-card rendering, and Rasenmaeher user-callback flow are validated from the local-only `cryptpad-development` branch in `/home/elderx/dev/docker-rasenmaeher-integration`.

## Current State

At the moment this stack is up locally and responding on all three local hosts. To get the current first-admin onboarding URL for the active data set, run:

```bash
docker compose logs --no-color cryptpad
```
