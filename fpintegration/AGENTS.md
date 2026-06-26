# AGENTS.md — python-rasenmaeher-fpapi (fpintegration)

## Purpose
The **reference product integration API** for Deploy App (RASENMAEHER). `fpintegration` is a
template / fake-product implementation that demonstrates how to write a new service integration.
It shows the exact API contract a product must implement to participate in the Deploy App
ecosystem (user lifecycle callbacks, UI card endpoint, mTLS setup). When adding a new real
service integration, copy this repo as a starting point.

## Stack & Key Technologies
- **Language:** Python 3.11
- **Framework:** FastAPI + Uvicorn
- **Key libs:** libpvarki (internal), pydantic v2
- **Testing:** pytest, tox (55% minimum coverage)
- **Linting:** pre-commit, pylint
- **Container:** Docker multi-target (devel_shell, tox, production)
- **Port:** 8001

## Development Setup
```bash
export DOCKER_BUILDKIT=1
# Linux SSH agent forwarding:
export DOCKER_SSHAGENT="-v $SSH_AUTH_SOCK:$SSH_AUTH_SOCK -e SSH_AUTH_SOCK"

docker build --ssh default --target devel_shell -t rasenmaeher_fpapi:devel_shell .
docker create --name rasenmaeher_fpapi_devel -v $(pwd):/app -p 8001:8001 \
  -it $(echo $DOCKER_SSHAGENT) rasenmaeher_fpapi:devel_shell
docker start -i rasenmaeher_fpapi_devel
```

## Running Tests
```bash
# Via tox (CI)
docker build --ssh default --target tox -t rasenmaeher_fpapi:tox .
docker run --rm -it -v $(pwd):/app $(echo $DOCKER_SSHAGENT) rasenmaeher_fpapi:tox

# Direct pytest inside devel_shell
pytest tests/ -v --cov=rasenmaeher_fpapi --cov-fail-under=55

# Pre-commit
pre-commit install --install-hooks
pre-commit run --all-files
```

## Code Conventions
- Follow pylint rules from root `pylintrc`
- New product integrations should replicate this repo's structure and naming pattern

## Architecture Notes
**Integration API contract** (endpoints every product integration must implement):
- `POST /api/v1/users/created` — Called when a user is enrolled; provision access
- `POST /api/v1/users/revoked` — Called when a user is removed; revoke access
- `POST /api/v1/users/promoted` — Called when a user is given admin role
- `POST /api/v1/users/demoted` — Called when admin role is removed
- `GET  /api/v1/ui/description` — Returns JSON card data for the Deploy App UI

**mTLS:** All POST endpoints from `rmapi` arrive via `productsnginx` with a client certificate
whose CN matches the `rmapi` service certificate. Validate this CN in your middleware.

**Shared volume:** Product credentials are written by miniwerk to the
`kraftwerk_shared_fake` volume at `/pvarki/kraftwerk-rasenmaeher-init.json`. Read this on
startup to get domain config and certificates.

**This is a fake product.** The `fpintegration` service does not manage any real resources —
it only validates the integration contract. Use it to test the full enrollment flow without
a real product backend.

## Common Agent Pitfalls
1. **This repo is a template, not a real product.** Do not add business logic here. Clone it
   for new real integrations; leave `fpintegration` as the reference implementation.
2. **mTLS certificates are required for all user lifecycle callbacks.** If you skip mTLS
   validation in your middleware, `rmapi` will still send client certs and a wrong CN will cause
   confusing `403` errors that look like network problems.
3. **The `kraftwerk_shared_fake` volume is specific to this fake product.** Real products get
   their own named volume (`kraftwerk_shared_<product>`). Copy the volume config from
   `docker-compose-local.yml` — do not reuse the fake product's volume.
4. **Coverage threshold is 55%.** Any new route without tests will fail CI.

## Related Repos
- https://github.com/pvarki/docker-rasenmaeher-integration (orchestration root)
- https://github.com/pvarki/python-rasenmaeher-api (calls the lifecycle callbacks)
- https://github.com/pvarki/python-miniwerk (writes the kraftwerk manifest)
