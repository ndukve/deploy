ARG NODE_IMAGE=node:20-bookworm-slim@sha256:17281e8d1dc4d671976c6b89a12f47a44c2f390b63a989e2e327631041f544fd
ARG PYTHON_IMAGE=python:3.11-slim-bookworm@sha256:420310dd2ff7895895f0f1f9d15cae5a95dabceb8f1d6b9a23ef33c2c1c542c3

FROM ${NODE_IMAGE} AS ui-builder

WORKDIR /build/rmcryptpad/ui

COPY rmcryptpad/ui/package.json rmcryptpad/ui/pnpm-lock.yaml ./
RUN npm install -g pnpm@10 \
    && pnpm install --frozen-lockfile

COPY rmcryptpad/ui/ ./
RUN pnpm build

FROM ${PYTHON_IMAGE} AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY rmcryptpad/pyproject.toml rmcryptpad/README.md /app/
COPY rmcryptpad/src /app/src
COPY rmcryptpad/docker /app/docker
COPY --from=ui-builder /build/rmcryptpad/ui/dist /opt/ui/cryptpad

RUN useradd --create-home --shell /usr/sbin/nologin --uid 4001 rmcryptpad \
    && pip install --no-cache-dir .

USER rmcryptpad

ENTRYPOINT ["/app/docker/entrypoint.sh"]
CMD ["rmcryptpad"]
