# CryptPad Rasenmaeher Integration Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Add a MediaMTX-style Rasenmaeher integration layer to this repository so upstream CryptPad stays untouched while users authenticate through mTLS-backed OIDC and Deploy App can render a CryptPad product card.

**Architecture:** Build a new `rmcryptpad` sidecar in this repo with FastAPI, PostgreSQL persistence, a minimal OIDC provider, and a federated UI bundle. Wire upstream CryptPad to the official SSO plugin, keep the sidecar responsible for Rasenmaeher product endpoints and live cert-to-callsign checks, and extend the local Docker Compose stack so the product can be verified in isolation before the larger stack points at this repo as a submodule.

**Tech Stack:** FastAPI, SQLModel, PostgreSQL, Authlib, Vite module federation, Docker Compose, Nginx, official `cryptpad/sso`

---

## Ground Rules For Implementation

- Keep CryptPad upstream code unmodified. Only adjust image build, mounted config, and reverse-proxy wiring in this repo.
- Treat `callsign` as the canonical CryptPad identity. Use it as the OIDC `sub` and the visible username/display seed.
- Treat `/api/v1/users/updated` as non-migrating. Same callsign may refresh cert metadata; a different callsign becomes a different CryptPad identity with no access to the old one.
- Keep `uuid` as supporting metadata only. Do not key CryptPad identity or OIDC `sub` off UUID.
- Keep Rasenmaeher-style API routes mTLS-header protected, but do not require transport-layer client certificates on OIDC discovery, token, userinfo, or JWKS.
- Let the larger integration stack override public URLs to `mtls.*` hosts later. This repo should expose public URL env vars instead of hardcoding them.

### Task 1: Scaffold The `rmcryptpad` Backend Package

**Files:**
- Create: `rmcryptpad/pyproject.toml`
- Create: `rmcryptpad/README.md`
- Create: `rmcryptpad/Dockerfile`
- Create: `rmcryptpad/docker/entrypoint.sh`
- Create: `rmcryptpad/docker/entrypoint-test.sh`
- Create: `rmcryptpad/src/rmcryptpad/__init__.py`
- Create: `rmcryptpad/src/rmcryptpad/py.typed`
- Create: `rmcryptpad/src/rmcryptpad/config.py`
- Create: `rmcryptpad/src/rmcryptpad/console.py`
- Create: `rmcryptpad/src/rmcryptpad/web/application.py`
- Create: `rmcryptpad/tests/conftest.py`
- Create: `rmcryptpad/tests/test_package.py`
- Modify: `Manual.MD`

**Step 1: Write the failing package and settings tests**

```python
from rmcryptpad import __version__
from rmcryptpad.config import RMCryptPadSettings


def test_version() -> None:
    assert __version__ == "0.1.0"


def test_settings_defaults() -> None:
    settings = RMCryptPadSettings.singleton()
    assert settings.rmcn == "rasenmaeher"
    assert settings.public_url == "https://cryptpad.localhost:8443"
    assert settings.public_sandbox_url == "https://sandbox.cryptpad.localhost:8443"
    assert settings.oidc_issuer == "https://rmcryptpad.localhost:8443"
```

**Step 2: Run test to verify it fails**

Run: `cd rmcryptpad && poetry run pytest tests/test_package.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'rmcryptpad'`

**Step 3: Write the minimal package/config implementation**

```python
__version__ = "0.1.0"


class RMCryptPadSettings(BaseSettings):
    rmcn: str = "rasenmaeher"
    public_url: str = "https://cryptpad.localhost:8443"
    public_sandbox_url: str = "https://sandbox.cryptpad.localhost:8443"
    oidc_issuer: str = "https://rmcryptpad.localhost:8443"
```

Implement the matching `FastAPI` app factory in `rmcryptpad/src/rmcryptpad/web/application.py` and a `rmcryptpad` CLI entrypoint in `rmcryptpad/src/rmcryptpad/console.py` so later tests can import the app without booting Docker.

**Step 4: Run test to verify it passes**

Run: `cd rmcryptpad && poetry run pytest tests/test_package.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rmcryptpad/pyproject.toml rmcryptpad/README.md rmcryptpad/Dockerfile rmcryptpad/docker rmcryptpad/src rmcryptpad/tests Manual.MD
git commit -m "feat: scaffold rmcryptpad service"
```

### Task 2: Add PostgreSQL Persistence For Callsigns, Products, And OIDC Codes

**Files:**
- Create: `rmcryptpad/src/rmcryptpad/db/__init__.py`
- Create: `rmcryptpad/src/rmcryptpad/db/base.py`
- Create: `rmcryptpad/src/rmcryptpad/db/engine.py`
- Create: `rmcryptpad/src/rmcryptpad/db/errors.py`
- Create: `rmcryptpad/src/rmcryptpad/db/dbinit.py`
- Create: `rmcryptpad/src/rmcryptpad/db/user.py`
- Create: `rmcryptpad/src/rmcryptpad/db/product.py`
- Create: `rmcryptpad/src/rmcryptpad/db/oidc_code.py`
- Create: `rmcryptpad/tests/docker-compose.yml`
- Create: `rmcryptpad/tests/test_orm.py`
- Modify: `rmcryptpad/tests/conftest.py`
- Modify: `rmcryptpad/src/rmcryptpad/config.py`

**Step 1: Write the failing ORM tests**

```python
@pytest.mark.asyncio
async def test_callsign_is_identity(dbinstance: None) -> None:
    created = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem="-----BEGIN CERTIFICATE-----\\nA\\n-----END CERTIFICATE-----\\n",
    )
    refreshed = await User.create_or_update(
        callsign="VIRTA-1",
        rmuuid="uuid-a",
        cert_pem="-----BEGIN CERTIFICATE-----\\nB\\n-----END CERTIFICATE-----\\n",
    )
    assert created.pk == refreshed.pk
    assert refreshed.cert_pem.endswith("B\\n-----END CERTIFICATE-----\\n")


@pytest.mark.asyncio
async def test_new_callsign_stays_separate(dbinstance: None) -> None:
    await User.create_or_update(callsign="VIRTA-1", rmuuid="uuid-a", cert_pem="A")
    await User.create_or_update(callsign="VIRTA-2", rmuuid="uuid-a", cert_pem="B")
    assert await User.by_callsign("VIRTA-1")
    assert await User.by_callsign("VIRTA-2")
```

**Step 2: Run test to verify it fails**

Run: `cd rmcryptpad && poetry run pytest tests/test_orm.py -v`
Expected: FAIL because the DB models and `dbinstance` fixture do not exist yet

**Step 3: Write the minimal persistence layer**

```python
class User(ORMBaseModel, table=True):
    __tablename__ = "users"

    callsign: str = Field(index=True, unique=True)
    rmuuid: str = Field(index=True)
    cert_pem: str
    cert_fingerprint: str | None = Field(default=None, index=True)
    is_rmadmin: bool = False
    revoked: datetime.datetime | None = Field(default=None, index=True)
```

Add:
- `DBSettings` with `RMCRYPTPAD_DATABASE_*` env support.
- `init_db()` and `drop_db()` helpers.
- `Product` model for `/api/v1/interop/*`.
- `OIDCAuthorizationCode` model storing hashed one-time codes, redirect URI, nonce, expiry, and used timestamp.
- A test Postgres service in `rmcryptpad/tests/docker-compose.yml`, mirroring `mtxauthz/tests/docker-compose.yml`.

**Step 4: Run test to verify it passes**

Run: `cd rmcryptpad && poetry run pytest tests/test_orm.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rmcryptpad/src/rmcryptpad/db rmcryptpad/tests/conftest.py rmcryptpad/tests/docker-compose.yml rmcryptpad/tests/test_orm.py rmcryptpad/src/rmcryptpad/config.py
git commit -m "feat: add rmcryptpad persistence layer"
```

### Task 3: Implement The Rasenmaeher Product Contract

**Files:**
- Create: `rmcryptpad/src/rmcryptpad/schema/__init__.py`
- Create: `rmcryptpad/src/rmcryptpad/schema/clients.py`
- Create: `rmcryptpad/src/rmcryptpad/schema/interop.py`
- Create: `rmcryptpad/src/rmcryptpad/web/security.py`
- Create: `rmcryptpad/src/rmcryptpad/web/usercrud.py`
- Create: `rmcryptpad/src/rmcryptpad/web/interop.py`
- Create: `rmcryptpad/src/rmcryptpad/web/description.py`
- Create: `rmcryptpad/src/rmcryptpad/web/instructions.py`
- Create: `rmcryptpad/src/rmcryptpad/web/clients.py`
- Create: `rmcryptpad/src/rmcryptpad/web/health.py`
- Modify: `rmcryptpad/src/rmcryptpad/web/application.py`
- Create: `rmcryptpad/tests/test_usercrud.py`
- Create: `rmcryptpad/tests/test_interop.py`
- Create: `rmcryptpad/tests/test_description.py`
- Create: `rmcryptpad/tests/test_clients.py`

**Step 1: Write the failing route tests**

```python
def test_client_data_returns_public_urls(testclient: TestClient) -> None:
    response = testclient.post("/api/v2/clients/data", json={})
    assert response.status_code == 200
    assert response.json()["data"]["url"] == "https://cryptpad.localhost:8443"
    assert response.json()["data"]["sandbox_url"] == "https://sandbox.cryptpad.localhost:8443"


def test_description_v2_exposes_component(testclient: TestClient) -> None:
    response = testclient.get("/api/v2/description/en")
    assert response.status_code == 200
    payload = response.json()
    assert payload["shortname"] == "cryptpad"
    assert payload["component"]["type"] == "component"
    assert payload["component"]["ref"] == "/ui/cryptpad/remoteEntry.js"
```

**Step 2: Run test to verify it fails**

Run: `cd rmcryptpad && poetry run pytest tests/test_usercrud.py tests/test_interop.py tests/test_description.py tests/test_clients.py -v`
Expected: FAIL with missing routers and/or `404 Not Found`

**Step 3: Write the minimal RM API implementation**

```python
router = APIRouter(dependencies=[Depends(MTLSHeader(auto_error=True))])


@router.post("/created")
async def user_created(user: UserCRUDRequest, request: Request) -> OperationResultResponse:
    comes_from_rm(request)
    await User.create_or_update(callsign=user.callsign, rmuuid=user.uuid, cert_pem=user.x509cert)
    return OperationResultResponse(success=True)
```

Implement:
- `comes_from_rm()` in `web/security.py` using `X-ClientCert-DN`.
- `/api/v1/users/{created,revoked,promoted,demoted}` keyed by callsign.
- `/api/v1/users/updated` so same-callsign updates refresh cert metadata, while a different callsign stays separate.
- `/api/v1/interop/add` and `/api/v1/interop/authz`.
- `/api/v1/instructions/{language}` with a small CryptPad-focused onboarding payload.
- `/api/v1/healthcheck`.
- `/api/v1/description/{language}` and `/api/v2/description/{language}` returning `shortname="cryptpad"` and `component.ref="/ui/cryptpad/remoteEntry.js"`.
- `/api/v2/clients/data` and `/api/v2/admin/clients/data` returning `{data: {url, sandbox_url, docs_url, oidc_issuer}}`.

**Step 4: Run test to verify it passes**

Run: `cd rmcryptpad && poetry run pytest tests/test_usercrud.py tests/test_interop.py tests/test_description.py tests/test_clients.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rmcryptpad/src/rmcryptpad/schema rmcryptpad/src/rmcryptpad/web rmcryptpad/tests/test_usercrud.py rmcryptpad/tests/test_interop.py rmcryptpad/tests/test_description.py rmcryptpad/tests/test_clients.py
git commit -m "feat: add rmcryptpad product api"
```

### Task 4: Implement The Minimal OIDC Provider For CryptPad SSO

**Files:**
- Create: `rmcryptpad/src/rmcryptpad/oidc/__init__.py`
- Create: `rmcryptpad/src/rmcryptpad/oidc/keys.py`
- Create: `rmcryptpad/src/rmcryptpad/oidc/tokens.py`
- Create: `rmcryptpad/src/rmcryptpad/web/oidc.py`
- Modify: `rmcryptpad/src/rmcryptpad/config.py`
- Modify: `rmcryptpad/src/rmcryptpad/web/application.py`
- Create: `rmcryptpad/tests/test_oidc.py`
- Modify: `rmcryptpad/tests/conftest.py`

**Step 1: Write the failing OIDC tests**

```python
def test_discovery_document(testclient: TestClient) -> None:
    response = testclient.get("/.well-known/openid-configuration")
    assert response.status_code == 200
    payload = response.json()
    assert payload["issuer"] == "https://rmcryptpad.localhost:8443"
    assert payload["authorization_endpoint"].endswith("/oidc/authorize")


def test_authorize_requires_live_callsign_header(unauth_testclient: TestClient) -> None:
    response = unauth_testclient.get("/oidc/authorize", params={"client_id": "cryptpad", "response_type": "code"})
    assert response.status_code == 403
```

**Step 2: Run test to verify it fails**

Run: `cd rmcryptpad && poetry run pytest tests/test_oidc.py -v`
Expected: FAIL with missing OIDC routes

**Step 3: Write the minimal OIDC implementation**

```python
@router.get("/oidc/authorize")
async def authorize(request: Request, client_id: str, redirect_uri: str, state: str, nonce: str | None = None):
    callsign = require_active_callsign(request)
    code = await OIDCAuthorizationCode.issue(
        callsign=callsign,
        client_id=client_id,
        redirect_uri=redirect_uri,
        nonce=nonce,
    )
    return RedirectResponse(f"{redirect_uri}?code={code}&state={quote(state)}", status_code=302)
```

Implement:
- Persistent RSA signing key management in `oidc/keys.py`, stored under a mounted directory such as `/data/oidc`.
- `/.well-known/openid-configuration`, `/oidc/jwks.json`, `/oidc/authorize`, `/oidc/token`, and `/oidc/userinfo`.
- Client authentication with env-configured `RMCRYPTPAD_OIDC_CLIENT_ID` and `RMCRYPTPAD_OIDC_CLIENT_SECRET`.
- `sub`, `preferred_username`, and `name` claims all sourced from the active callsign.
- `require_active_callsign()` so browser authorize requests must carry a forwarded `X-ClientCert-DN` whose CN matches an active callsign row.
- Token/userinfo flows that do not require `MTLSHeader`, because CryptPad backend will call them server-to-server.

**Step 4: Run test to verify it passes**

Run: `cd rmcryptpad && poetry run pytest tests/test_oidc.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add rmcryptpad/src/rmcryptpad/oidc rmcryptpad/src/rmcryptpad/web/oidc.py rmcryptpad/src/rmcryptpad/config.py rmcryptpad/src/rmcryptpad/web/application.py rmcryptpad/tests/test_oidc.py rmcryptpad/tests/conftest.py
git commit -m "feat: add rmcryptpad oidc provider"
```

### Task 5: Add The Federated CryptPad Product Card UI

**Files:**
- Create: `rmcryptpad/ui/package.json`
- Create: `rmcryptpad/ui/pnpm-lock.yaml`
- Create: `rmcryptpad/ui/tsconfig.json`
- Create: `rmcryptpad/ui/vite.config.ts`
- Create: `rmcryptpad/ui/index.html`
- Create: `rmcryptpad/ui/src/App.tsx`
- Create: `rmcryptpad/ui/src/main.tsx`
- Create: `rmcryptpad/ui/src/App.test.tsx`
- Create: `rmcryptpad/ui/src/index.css`
- Create: `rmcryptpad/ui/src/lib/metadata.ts`
- Create: `rmcryptpad/ui/public/cryptpad-mark.svg`
- Modify: `rmcryptpad/Dockerfile`

**Step 1: Write the failing UI test**

```tsx
import { render, screen } from "@testing-library/react";
import App from "./App";

test("renders an open button for CryptPad", () => {
  render(
    <App
      data={{ url: "https://mtls.cryptpad.example.invalid", sandbox_url: "https://mtls.sandbox.cryptpad.example.invalid" }}
      meta={{ callsign: "VIRTA-1", theme: "light" }}
    />,
  );
  expect(screen.getByRole("link", { name: /open cryptpad/i })).toHaveAttribute(
    "href",
    "https://mtls.cryptpad.example.invalid",
  );
});
```

**Step 2: Run test to verify it fails**

Run: `cd rmcryptpad/ui && pnpm test -- --run App.test.tsx`
Expected: FAIL because the UI files and test tooling do not exist yet

**Step 3: Write the minimal federated component**

```tsx
export default function App({ data, meta }: Props) {
  return (
    <section className="cryptpad-card">
      <p className="eyebrow">Certificate-backed collaboration</p>
      <h1>CryptPad</h1>
      <p>Signed in as {meta.callsign}</p>
      <a href={data.url}>Open CryptPad</a>
    </section>
  );
}
```

Configure module federation in `rmcryptpad/ui/vite.config.ts` so it exposes `./src/App.tsx` as `remoteEntry.js`, and update `rmcryptpad/Dockerfile` to build the UI in a multi-stage build and copy the static output into the runtime image under `/opt/ui/cryptpad`.

**Step 4: Run test and build to verify it passes**

Run: `cd rmcryptpad/ui && pnpm test -- --run App.test.tsx && pnpm build`
Expected: PASS and `dist/remoteEntry.js` exists

**Step 5: Commit**

```bash
git add rmcryptpad/ui rmcryptpad/Dockerfile
git commit -m "feat: add cryptpad federated product card"
```

### Task 6: Install And Configure The Official CryptPad SSO Plugin

**Files:**
- Create: `config/sso.js`
- Modify: `docker/cryptpad/Dockerfile`
- Modify: `compose.yaml`
- Modify: `config/config.js`
- Modify: `README.md`
- Create: `tests/test_cryptpad_image.sh`

**Step 1: Write the failing image/config verification**

```bash
#!/bin/sh
set -eu

docker build -f docker/cryptpad/Dockerfile -t local/cryptpad-sso-test .
docker run --rm local/cryptpad-sso-test sh -lc '
  test -d /cryptpad/lib/plugins/sso &&
  test -f /cryptpad/config/sso.js
'
```

**Step 2: Run verification to confirm it fails**

Run: `sh tests/test_cryptpad_image.sh`
Expected: FAIL because the SSO plugin and `config/sso.js` are not in the image

**Step 3: Write the minimal CryptPad SSO wiring**

```js
module.exports = {
  enabled: true,
  enforced: true,
  cpPassword: false,
  forceCpPassword: false,
  list: [
    {
      name: process.env.CPAD_SSO_NAME || 'rmcryptpad',
      type: 'oidc',
      url: process.env.CPAD_SSO_ISSUER || 'https://rmcryptpad.localhost:8443',
      client_id: process.env.CPAD_SSO_CLIENT_ID || 'cryptpad',
      client_secret: process.env.CPAD_SSO_CLIENT_SECRET || 'change-me',
      username_claim: 'preferred_username',
      id_token_alg: 'RS256',
      userinfo_token_alg: 'RS256',
      use_pkce: true,
      use_nonce: true,
    },
  ],
};
```

Modify `docker/cryptpad/Dockerfile` to clone a compatible `cryptpad/sso` tag into `/cryptpad/lib/plugins/sso`, copy `config/sso.js` into the image, and expose a `CRYPTPAD_SSO_VERSION` build arg so CryptPad and plugin versions can be upgraded together.

**Step 4: Re-run verification**

Run: `sh tests/test_cryptpad_image.sh`
Expected: PASS

**Step 5: Commit**

```bash
git add config/sso.js docker/cryptpad/Dockerfile compose.yaml config/config.js README.md tests/test_cryptpad_image.sh
git commit -m "feat: wire cryptpad to official sso plugin"
```

### Task 7: Extend Local Compose, Nginx, And Runtime Wiring

**Files:**
- Modify: `compose.yaml`
- Modify: `docker/nginx/nginx.conf`
- Modify: `docker/nginx/Dockerfile`
- Modify: `docker/scripts/generate-local-cert.sh`
- Modify: `docker/scripts/prepare-bind-mounts.sh`
- Create: `volumes/rmcryptpad/.gitkeep`
- Create: `volumes/postgres/.gitkeep`

**Step 1: Write the failing runtime checks**

```bash
docker compose config
docker compose up -d --build postgres rmcryptpad cryptpad nginx
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://rmcryptpad.localhost:8443/.well-known/openid-configuration
curl --cacert volumes/nginx/certs/cryptpad.local.pem -I https://cryptpad.localhost:8443/ssoauth
```

**Step 2: Run the checks to verify they fail**

Run: the command block above
Expected: `docker compose` fails because `postgres` and `rmcryptpad` services do not exist yet, or `curl` fails with `Could not resolve host` / `404`

**Step 3: Write the minimal runtime wiring**

```yaml
postgres:
  image: postgres:17-alpine
  environment:
    POSTGRES_DB: ${RMCRYPTPAD_DATABASE_DATABASE:-rmcryptpad}
    POSTGRES_USER: ${RMCRYPTPAD_DATABASE_USER:-rmcryptpad}
    POSTGRES_PASSWORD: ${RMCRYPTPAD_DATABASE_PASSWORD:-change-me}

rmcryptpad:
  build:
    context: ./rmcryptpad
  environment:
    RMCRYPTPAD_PUBLIC_URL: ${RMCRYPTPAD_PUBLIC_URL:-https://cryptpad.localhost:8443}
    RMCRYPTPAD_PUBLIC_SANDBOX_URL: ${RMCRYPTPAD_PUBLIC_SANDBOX_URL:-https://sandbox.cryptpad.localhost:8443}
    RMCRYPTPAD_OIDC_ISSUER: ${RMCRYPTPAD_OIDC_ISSUER:-https://rmcryptpad.localhost:8443}
```

Also:
- Mount a persistent key directory for OIDC signing material.
- Proxy `rmcryptpad.localhost` through the local nginx container.
- Add `rmcryptpad.localhost` to the self-signed certificate SAN list.
- Keep the existing standalone local CryptPad origin defaults intact, but make all public URLs overrideable for the future `mtls.*` deployment.

**Step 4: Re-run the checks**

Run: the command block from Step 1
Expected: `docker compose config` passes, the services start, and the two `curl` requests return `HTTP/2 200` or `HTTP/2 302`

**Step 5: Commit**

```bash
git add compose.yaml docker/nginx/nginx.conf docker/nginx/Dockerfile docker/scripts/generate-local-cert.sh docker/scripts/prepare-bind-mounts.sh volumes/rmcryptpad/.gitkeep volumes/postgres/.gitkeep
git commit -m "feat: add local runtime wiring for rmcryptpad"
```

### Task 8: Update Operator Docs And Run Full Verification

**Files:**
- Modify: `Manual.MD`
- Modify: `README.md`
- Modify: `docs/plans/2026-03-18-cryptpad-rasenmaeher-design.md`

**Step 1: Write the failing documentation checklist**

```text
- Missing rmcryptpad bootstrap commands
- Missing local env vars for CryptPad SSO and rmcryptpad Postgres
- Missing note that full browser mTLS smoke belongs to the larger integration stack
```

**Step 2: Run the full verification suite before touching docs**

Run:

```bash
cd rmcryptpad && poetry run pytest -v
cd ../rmcryptpad/ui && pnpm test -- --run && pnpm build
cd ../.. && sh tests/test_cryptpad_image.sh
docker compose config
docker compose up -d --build
docker compose ps
curl --cacert volumes/nginx/certs/cryptpad.local.pem https://rmcryptpad.localhost:8443/.well-known/openid-configuration
```

Expected: all commands pass

**Step 3: Update the docs**

Add:
- A new `Manual.MD` status line showing that the implementation plan exists and that execution is the next step.
- A root `README.md` section describing `cryptpad`, `sandbox`, and `rmcryptpad`.
- A note in the design doc clarifying that standalone repo-local verification covers product services, while full browser mTLS login is validated from the local-only `cryptpad-development` branch in `/home/elderx/dev/docker-rasenmaeher-integration`.

**Step 4: Re-run the verification suite**

Run: the command block from Step 2
Expected: still all green after docs changes

**Step 5: Commit**

```bash
git add Manual.MD README.md docs/plans/2026-03-18-cryptpad-rasenmaeher-design.md
git commit -m "docs: capture rmcryptpad operator workflow"
```

## Final Execution Checkpoint

After Task 8:
- Request a code review before any push from the `cryptpad-rasenmaeher-integration` worktree.
- Do not change `/home/elderx/dev/docker-rasenmaeher-integration` yet, except for local-only smoke verification on the already-created `cryptpad-development` branch after this repo is complete.
- When the product repo is green, the follow-up work is to point the integration repo’s `cryptpad` submodule at this branch and wire the outer `productsnginx` routes to the new `rmcryptpad`, `cryptpad`, and `sandbox` services without pushing that repo.
