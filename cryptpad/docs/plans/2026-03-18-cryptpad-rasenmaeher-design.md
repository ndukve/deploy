# CryptPad Rasenmaeher Integration Design

## Goal

Integrate CryptPad into the Deploy App / Rasenmaeher stack without modifying CryptPad upstream code, while preserving the existing mTLS-based access model and the MediaMTX-style product integration pattern.

## Constraints

- CryptPad upstream must stay updateable without carrying local source patches.
- The product must expose the same Rasenmaeher-facing integration contract used by existing products.
- Human access must follow the stack's `mtls.<product>.<domain>` hostname convention.
- CryptPad identity is keyed by `callsign`.
- Callsigns are treated as immutable inside CryptPad for v1.
- A new callsign must never inherit the previous callsign's CryptPad data.
- The sidecar should use PostgreSQL like `rmmtx`.

## Upstream Basis

- CryptPad will use the official CryptPad SSO plugin instead of a custom authentication fork.
- The sidecar will act as a small OpenID Connect provider for CryptPad.
- CryptPad will be configured for SSO-driven account access with no additional CryptPad password in v1.

References:

- <https://github.com/cryptpad/sso>
- <https://docs.cryptpad.org/en/admin_guide/admin_panel.html>

## Architecture

The integration follows the same split as MediaMTX:

- `cryptpad-app`: upstream CryptPad application container.
- `cryptpad-nginx`: CryptPad-specific reverse proxy for main origin, sandbox origin, and websocket forwarding.
- `rmcryptpad`: product integration sidecar.
- `cryptpad-ui`: a small optional remote UI bundle for the Deploy App product card.

The `cryptpad` repository owns these pieces. The `docker-rasenmaeher-integration` repository should only consume this repository as a submodule and wire the services into the larger composition.

## Hostnames

Canonical user-facing hosts:

- `https://mtls.cryptpad.${SERVER_DOMAIN}`
- `https://mtls.sandbox.cryptpad.${SERVER_DOMAIN}`

Internal / auxiliary hosts:

- `https://cryptpad.${SERVER_DOMAIN}`
- `https://sandbox.cryptpad.${SERVER_DOMAIN}`
- `https://rmcryptpad.${SERVER_DOMAIN}`

The user-facing product card and any generated product links must prefer the `mtls.` CryptPad hosts to match the current stack convention for authenticated product access.

## Identity Model

- Canonical CryptPad identity: `callsign`
- Live access proof: mTLS client certificate CN
- Supporting metadata only: RM `uuid`, delivered `x509cert`, role flags

`rmcryptpad` issues OIDC claims with:

- `sub = <callsign>`
- display name / username claim = `<callsign>`

This makes one CryptPad account per callsign. If a callsign changes in Rasenmaeher, CryptPad treats the new callsign as a different identity with no access to the old callsign's account or documents.

## User Lifecycle

Rasenmaeher-facing sidecar endpoints:

- `POST /api/v1/users/created`
- `POST /api/v1/users/revoked`
- `POST /api/v1/users/promoted`
- `POST /api/v1/users/demoted`
- `PUT /api/v1/users/updated`

Behavior:

- `created`: create or re-enable the callsign record
- `revoked`: disable the callsign and reject future OIDC login
- `promoted`: record RM admin state for future use
- `demoted`: remove RM admin marker
- `updated`: record the event, but do not migrate data; the old and new callsigns remain separate

CryptPad server-admin privileges are out of scope for v1. RM admin state may be exposed in the sidecar API or UI later, but it does not automatically make users CryptPad instance administrators.

## rmcryptpad Responsibilities

The sidecar has two roles:

1. Product integration API
- expose `interop`, `users`, `description`, `instructions`, `clients/data`, and health endpoints expected by Rasenmaeher

2. OIDC provider for CryptPad
- discovery document
- authorization endpoint
- token endpoint
- userinfo endpoint
- JWKS endpoint

The sidecar should be implemented as a FastAPI service with SQLModel and PostgreSQL, staying close to the `rmmtx` structure where practical.

## OIDC Flow

1. User enters Deploy App with mTLS and opens the CryptPad product.
2. The Deploy App product page loads CryptPad product metadata and UI from `rmcryptpad`.
3. The product UI sends the user to `https://mtls.cryptpad.${SERVER_DOMAIN}`.
4. `productsnginx` validates client mTLS and proxies to the CryptPad product stack.
5. CryptPad starts SSO and redirects to `rmcryptpad`.
6. `rmcryptpad` authorize flow validates the forwarded client cert identity and resolves the live callsign.
7. `rmcryptpad` issues an OIDC code for that callsign.
8. CryptPad exchanges the code at `rmcryptpad` token endpoint.
9. `rmcryptpad` returns tokens and userinfo for the callsign.
10. CryptPad creates or reuses the SSO-backed account for that callsign.

Important nuance:

- OIDC backend endpoints cannot require browser mTLS, because CryptPad itself must call token and userinfo endpoints.
- Therefore `rmcryptpad` must separate transport-level access:
  - `/api/v1/*` and `/api/v2/*`: mTLS-protected product integration API
  - OIDC discovery / token / userinfo / JWKS: reachable without client cert
  - OIDC authorize: still validates the forwarded client certificate identity before issuing a code

## Persistence

`rmcryptpad` uses PostgreSQL for sidecar state, matching the MediaMTX integration pattern.

Expected stored state:

- callsign
- RM UUID
- delivered certificate PEM
- active / revoked flag
- RM admin flag
- timestamps
- temporary OIDC authorization state / code material as needed by the chosen OIDC library

CryptPad document state remains in CryptPad's own persistent data volume.

## Product UI

The product card should be delivered the same way as existing modular products:

- `/api/v2/description/{language}` advertises:
  - `shortname: "cryptpad"`
  - `component.type: "component"`
  - `component.ref: "/ui/cryptpad/remoteEntry.js"`

- `/api/v2/clients/data` returns a minimal payload:
  - `url`
  - `sandbox_url`
  - optional `docs_url`

The remote UI should stay intentionally small in v1:

- explain that CryptPad access is certificate-backed
- show the active callsign
- provide a clear "Open CryptPad" action
- optionally expose docs / troubleshooting links

## Local Testing Strategy

There are two local phases:

1. Standalone product-local testing in this repository
- bring up CryptPad, `cryptpad-nginx`, and `rmcryptpad`
- verify product services, OIDC discovery, SSO image wiring, UI asset delivery, and local runtime health

2. Full-stack local testing through `docker-rasenmaeher-integration`
- consume this repository as a submodule on the local-only `cryptpad-development` branch
- add the required product services and product host routing
- verify:
  - product card visibility
  - mTLS access through `productsnginx`
  - Rasenmaeher user callbacks
  - first-login CryptPad account creation by callsign
  - callsign revocation behavior

## Non-Goals For V1

- migrating CryptPad data between callsigns
- automatic CryptPad server-admin assignment from RM admin role
- storing additional profile fields from Rasenmaeher inside CryptPad
- modifying CryptPad upstream code
- non-SSO local signup / login inside CryptPad
