# Local CryptPad Docker Design

## Goal

Create a local-first CryptPad deployment that follows the official two-origin production model closely enough to validate behavior before integrating it into a larger Docker Compose stack.

## Constraints

- The directory starts empty.
- The setup must run with a single `docker compose up -d`.
- CryptPad requires a main origin and a sandbox origin for the recommended security model.
- The user wants fully local testing rather than depending on public DNS.
- The stack should stay close to the official installation guidance: CryptPad behind Nginx with HTTPS and websocket proxying.

## Chosen Approach

Use these two hostnames locally:

- `cryptpad.localhost:8443`
- `sandbox.cryptpad.localhost:8443`

This machine already resolves both names to loopback, which keeps the setup fully local without editing public DNS records. Nginx will terminate TLS for both names with one locally generated certificate that includes both SANs, then proxy HTTP traffic to the CryptPad app server and websocket traffic to the separate websocket port described in the official docs. The host publishes local HTTPS on port `8443` to reduce the chance of clashing with other software already using `443`.

## Architecture

- `cryptpad`: a pinned CryptPad 2025.9.0 container built from the official release source with a slim Node base, non-root runtime, persistent data mounts, and no OnlyOffice support for this first local step.
- `nginx`: a small Nginx reverse proxy container that serves both `cryptpad.localhost` and `sandbox.cryptpad.localhost`, generates a local certificate if needed on startup, and forwards `/cryptpad_websocket` to CryptPad's websocket port.
- `perm-init`: a one-shot helper that prepares writable bind-mounted directories for the CryptPad runtime UID so the stack can start with one Compose command.

## Security Notes

- The local stack uses two origins and HTTPS, matching the official sandbox model more closely than a plain `localhost:3000` development setup.
- The certificate will be locally generated, not publicly trusted. Browsers will show a warning until the cert is trusted or an exception is accepted once.
- Only the reverse proxy is published to the host. CryptPad's internal ports stay on the Docker network.
- Containers will run with the least privilege that is practical for this local setup: non-root for CryptPad, slim pinned base images, healthchecks, and minimal writable mounts.

## Configuration

- `config/config.js` will explicitly set `httpUnsafeOrigin` to `https://cryptpad.localhost` and `httpSafeOrigin` to `https://sandbox.cryptpad.localhost`.
- `customize/application_config.js` will set `loginSalt` before any accounts are created, per the official docs.
- Storage directories will be bind-mounted so the data layout remains visible and portable for the later larger composition.

## Verification

- `docker compose config` validates the Compose model.
- `docker compose up -d --build` boots the stack.
- `curl -kI https://cryptpad.localhost:8443` confirms HTTPS and Nginx routing.
- `curl -kI https://sandbox.cryptpad.localhost:8443` confirms the sandbox origin is served.
- `docker compose logs cryptpad` provides the onboarding URL/token.
- Visiting `https://cryptpad.localhost:8443/checkup/` validates the instance configuration after startup.

## Deferred For Later

- Trusted local CA automation such as `mkcert`
- OnlyOffice support
- Production certificate issuance
- Integration into the larger Compose deployment
