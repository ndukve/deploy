# AGENTS.md — docker-rasenmaeher-cfssl

## Purpose

Internal PKI for Deploy App (RASENMAEHER). Runs three components: the CFSSL certificate
authority (signs CSRs from services), the OCSP responder (provides certificate revocation
status), and `ocsprest` (a FastAPI wrapper around OCSP that adds a health-check endpoint).
All Deploy App services that need mTLS or signed certificates get them from cfssl.

## Stack & Key Technologies

- **cfssl / ocsp:** CloudFlare CFSSL (Go binary, bundled image)
- **ocsprest:** Python 3.11, FastAPI — thin wrapper adding `/healthcheck`
- **Key lib:** libpvarki (internal)
- **Testing:** pytest, tox (via ocsprest), prek (pre-commit-compatible runner)
- **Container targets:** `api` (cfssl), `ocsp`, `ocsprest`, `openapi` (spec dump)

## Development Setup

```bash
export DOCKER_BUILDKIT=1
# Linux:
export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"

# Build ocsprest devel shell
docker build --ssh default --target devel_shell -t ocsprest:devel_shell .
docker create --name ocsprest_devel -v $(pwd):/app \
  -it $(echo $DOCKER_SSHAGENT) ocsprest:devel_shell
docker start -i ocsprest_devel

# For cfssl health check:
curl cfssl info -remote http://127.0.0.1:8888

# Key env vars:
# CFSSL_CA_NAME       — Name of the CA (used in cert subject)
# CA_EXPIRY           — CA certificate lifetime (default: 2016h = 84 days)
# SIGN_DEFAULT_EXPIRY — Signed cert lifetime (default: 1008h = 42 days)
```

## Running Tests

```bash
# Via tox (CI)
docker build --ssh default --target tox -t ocsprest:tox .
docker run --rm -it -v $(pwd):/app $(echo $DOCKER_SSHAGENT) ocsprest:tox

# Direct pytest inside devel_shell
pytest tests/ -v

# Pre-commit (via prek)
prek install --install-hooks
prek run --all-files

# Dump OpenAPI spec
docker build --target openapi -t ocsprest:openapi .
docker run --rm ocsprest:openapi
```

## Code Conventions

- `ocsprest` follows the same `CFSSL_` env prefix pattern via pydantic `BaseSettings`
- Pre-commit hooks enforced via `prek`;

## Architecture Notes

**Three components, three ports:**

| Component | Port | Role                               |
| --------- | ---- | ---------------------------------- |
| cfssl     | 8888 | CA endpoint — signs CSRs           |
| ocsp      | 8889 | OCSP responder — revocation status |
| ocsprest  | 8887 | FastAPI health wrapper around OCSP |

**Shared volume `ca_public`:** cfssl writes `/ca_public/ca_chain.pem` which is the root CA
certificate. Every other service mounts this volume and uses the CA chain to validate TLS
connections. This is the single trust anchor for the entire deployment.

**Dependency:** cfssl depends on miniwerk being healthy (to have a cert available for the CA).
Services that need to sign CSRs depend on cfssl being healthy.

**CSR signing flow:** A service generates a keypair + CSR → calls `POST /api/v1/cfssl/sign`
(or directly `cfssl:8888/api/v1/cfssl/sign`) → receives signed cert → configures mTLS.

## Common Agent Pitfalls

1. **`ca_public` volume is the trust anchor.** Every service that does TLS validation mounts
   this volume. If you change CA config, all services need their cert chains regenerated — this
   usually requires `down -v` and a full restart.
2. **cfssl and ocsp are Go binaries, not Python.** Do not attempt to `pip install` anything for
   the cfssl or ocsp containers. Only `ocsprest` is Python.
3. **`CA_EXPIRY` and `SIGN_DEFAULT_EXPIRY` are in hours, not days.** Default signed cert
   lifetime is 1008h (~42 days). In local dev, short expiry means certs expire fast — this is
   intentional to test renewal flows.
4. **The `openapi` Docker target dumps the spec to stdout.** Use it with `docker run --rm` and
   redirect to a file; do not bake the spec into the image.

## Related Repos

- https://github.com/pvarki/docker-rasenmaeher-integration (orchestration root)
- https://github.com/pvarki/python-miniwerk (provides initial CA cert material)
- https://github.com/pvarki/python-rasenmaeher-api (primary CSR signer consumer)
