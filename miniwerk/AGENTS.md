# AGENTS.md — python-miniwerk

## Purpose

Minimal KRAFTWERK emulation for the Deploy App (RASENMAEHER) stack. miniwerk is the very
first service to start in the compose stack. It orchestrates TLS certificate provisioning
(Let's Encrypt in production, mkcert locally) and writes a per-product JSON manifest to
shared Docker volumes so every downstream service knows its domain, certificates, and secrets.
Nothing else can start until miniwerk is healthy.

## Stack & Key Technologies

- **Language:** Python 3.11
- **Framework:** Custom async (aiohttp-based)
- **Key libs:** libpvarki, cryptography, certbot / mkcert
- **Testing:** pytest, tox (65% minimum coverage)
- **Linting:** prek (drop-in pre-commit replacement), ruff, mypy, bandit
- **Container:** Docker multi-target (devel_shell, tox, production)
- **Port:** 80 (internal cert delivery)

## Development Setup

```bash
export DOCKER_BUILDKIT=1
# Linux:
export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"
# macOS:
# export DOCKER_SSHAGENT="-v /run/host-services/ssh-auth.sock:/run/host-services/ssh-auth.sock -e SSH_AUTH_SOCK=/run/host-services/ssh-auth.sock"

docker build --ssh default --target devel_shell -t miniwerk:devel_shell .
docker create --name miniwerk_devel -v $(pwd):/app -p 80:80 \
  -it $(echo $DOCKER_SSHAGENT) miniwerk:devel_shell
docker start -i miniwerk_devel

# Key env vars:
# MW_LE_EMAIL       — Let's Encrypt account email
# MW_LE_TEST=true   — Use LE staging (local dev); false for production
# MW_MKCERT=true    — Use mkcert instead of LE (fully local, no DNS needed)
# MW_PRODUCTS       — Comma-separated list of product names to provision
```

## Running Tests

```bash
# Via tox (CI)
docker build --ssh default --target tox -t miniwerk:tox .
docker run --rm -it -v $(pwd):/app $(echo $DOCKER_SSHAGENT) miniwerk:tox

# Direct pytest inside devel_shell
pytest tests/ -v --cov=miniwerk --cov-fail-under=65

# Pre-commit hooks (run via prek)
prek install --install-hooks
prek run --all-files
```

## Code Conventions

- Async-first: use `aiohttp` / `asyncio`, not `requests`
- Follow ruff rules configured in `pyproject.toml` (`[tool.ruff]`)

## Architecture Notes

**`src/miniwerk/config.py`** defines the
`MWConfig` settings model (read from `MW_*` env vars) and the per-product
`ProductSettings` defaults which products exist, which subdomains they own,
and which ports they listen on. Manifest generation, FQDN enumeration, and
certificate provisioning all read from here. Any change to which products
miniwerk supports starts in this file; env vars only override the defaults
defined there.

**Startup order:** miniwerk MUST be healthy before cfssl, postgres, keycloak, or any product
service starts. The compose health-check dependency chain enforces this.

**Certificate modes:**

- `MW_MKCERT=true` — Fully local; uses mkcert to generate self-signed certs. No DNS required.
  Used for unit/integration testing.
- `MW_LE_TEST=true` — Let's Encrypt staging. Requires real DNS but uses LE test CA (untrusted).
  Use this for manual integration testing against real DNS.
- `MW_LE_TEST=false` (production) — Real Let's Encrypt certificates. Requires all DNS records
  to be pointing at the server before miniwerk starts.

**Kraftwerk manifest pattern:** For each product in `MW_PRODUCTS`, miniwerk writes a JSON file
to `/pvarki/kraftwerk-rasenmaeher-init.json` inside the product's shared volume. The format:

```json
{ "dns": "product.yourdomain.fi", "products": { "tak": "tak.yourdomain.fi" } }
```

**Certificate outputs:**

- Let's Encrypt certs → `le_certs:/le_certs` Docker volume
- CA public cert → `ca_public:/ca_public/ca_chain.pem` (read by all services)

**Domains provisioned:** miniwerk handles: `domain`, `kc.domain`, `tak.domain`, `bl.domain`,
`mtx.domain`, `matrix.domain`, `mtls.domain`, and all `mtls.*` variants.

## Adding a New Product Integration

The set of changes is small but every step matters — skipping any of them will
break either tests, manifest generation, or TLS provisioning. Throughout this
section, replace `<new-product-name-here>` with the short-name of the product
you're adding (lowercase, no dots, matches what the rest of the stack will use
as the subdomain prefix e.g. `tak`, `bl`, `mtx`).

### 1. Register the product in `src/miniwerk/config.py`

- Append the short-name to the comma-separated `products` default. This string
  is the source of truth for which manifests get generated and which FQDNs get
  certificates. Pattern: `"fake,tak,bl,mtx,<new-product-name-here>"`.
- Add a new `ProductSettings` field on `MWConfig` with a `default_factory`:
  ```python
  <new-product-name-here>: ProductSettings = Field(
      description="Settings for <New Product> integration API",
      default_factory=lambda: ProductSettings(
          api_host="<new-product-name-here>",
          user_host="<new-product-name-here>",
          api_port=4626,
          user_port=4626,
      ),
  )
  ```
- Pick `api_port` / `user_port` to match the product's exposed listeners.
  Most internal APIs use `4626` (the standard mTLS API port). The user-facing
  port is whatever the product serves end users on — copy from a similar
  existing product rather than guessing.
- `api_host` / `user_host` are subdomain prefixes, they become
  `<host>.<MW_DOMAIN>`. Keep them identical to the product short-name unless
  there's a real reason to diverge (none of the existing products do).
- Do **not** add `kc` to the `products` list, it is appended programmatically
  and adding it manually will produce duplicate manifests.

### 2. Update `tests/test_config.py`

The FQDN test enumerates the exact set of hostnames miniwerk will request
certificates for. Add **both** the base FQDN and its `mtls.` variant for the
new product:

```
<new-product-name-here>.pytest.pvarki.fi
mtls.<new-product-name-here>.pytest.pvarki.fi
```

Also extend the expected `products` string in any test that asserts on the
default products list. If you skip this, the test fails noisily — which is the
correct behavior. Don't "fix" it by trimming the product back out.

### 3. Bump the version

Use bumpversion so all four locations stay in sync:

```bash
bumpversion patch    # or minor, if the integration is user-visible
```

This updates `.bumpversion.cfg`, `pyproject.toml`, `src/miniwerk/__init__.py`,
and `tests/test_miniwerk.py` together. Editing them by hand is a known source
of CI failures — let the tool do it.

### 4. Verify before opening a PR

Run the test suite (see the **Running Tests** section above) and confirm the
FQDN test in `tests/test_config.py` passes with the new product's base and
`mtls.` hostnames in the expected set. The FQDN test is the early warning that
something is off - if it passes, cert provisioning and manifest generation will
line up too.

### 5. Downstream consequences (no action in miniwerk, but plan ahead)

Adding a product here means the product's own service must:

- Be reachable at `<new-product-name-here>.<MW_DOMAIN>` and
  `mtls.<new-product-name-here>.<MW_DOMAIN>` (DNS records must exist before LE
  provisioning runs in production).
- Mount the shared `le_certs` and `ca_public` volumes to read its certs.
- Read its kraftwerk manifest from `/pvarki/kraftwerk-rasenmaeher-init.json`.

The compose file in
[docker-rasenmaeher-integration](https://github.com/pvarki/docker-rasenmaeher-integration)
is where those wiring changes land, not in miniwerk itself.

## Common Agent Pitfalls

1. **miniwerk MUST complete before anything else.** If you see other services crashing on
   startup with cert or manifest errors, wait for miniwerk to reach a healthy state first.
   Do not remove or weaken the health-check dependency in the compose file.
2. **`MW_MKCERT=true` is for local dev only.** Never use mkcert-generated certs in a
   production deployment — clients will not trust them.
3. **Changing `MW_PRODUCTS` requires a volume wipe.** If you add or remove a product from
   the list, existing manifests in the old volumes will conflict. Run `down -v` to wipe before
   bringing back up.
4. **Buildkit is required.** The Docker build will silently fail or produce an incorrect image
   without `DOCKER_BUILDKIT=1`. Always set it.
5. **On macOS the SSH agent socket path differs.** Use
   `/run/host-services/ssh-auth.sock` on macOS vs `$SSH_AUTH_SOCK` on Linux.

## Related Repos

- https://github.com/pvarki/docker-rasenmaeher-integration (orchestration root)
- https://github.com/pvarki/python-pvarki-cfssl (consumes the CA certs miniwerk prepares)
- https://github.com/pvarki/python-rasenmaeher-api (reads the kraftwerk manifest)
