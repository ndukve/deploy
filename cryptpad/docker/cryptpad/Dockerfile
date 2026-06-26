ARG NODE_IMAGE=node:22-bookworm-slim@sha256:4f77a690f2f8946ab16fe1e791a3ac0667ae1c3575c3e4d0d4589e9ed5bfaf3d
ARG CRYPTPAD_VERSION=2025.9.0
ARG CRYPTPAD_SSO_VERSION=0.4.0

FROM ${NODE_IMAGE} AS build

ARG CRYPTPAD_VERSION
ARG CRYPTPAD_SSO_VERSION

WORKDIR /tmp

RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://github.com/cryptpad/cryptpad/archive/refs/tags/${CRYPTPAD_VERSION}.tar.gz" -o cryptpad.tar.gz \
    && mkdir -p /src \
    && tar -xzf cryptpad.tar.gz -C /src --strip-components=1

RUN curl -fsSL "https://github.com/cryptpad/sso/archive/refs/tags/${CRYPTPAD_SSO_VERSION}.tar.gz" -o cryptpad-sso.tar.gz \
    && mkdir -p /src/lib/plugins/sso \
    && tar -xzf cryptpad-sso.tar.gz -C /src/lib/plugins/sso --strip-components=1

WORKDIR /src

RUN npm ci --omit=dev \
    && npm run install:components \
    && npm cache clean --force

FROM ${NODE_IMAGE} AS runtime

ENV NODE_ENV=production
ENV HOME=/cryptpad

RUN groupadd --gid 4001 cryptpad \
    && useradd --uid 4001 --gid 4001 --home-dir /cryptpad --create-home --shell /usr/sbin/nologin cryptpad

WORKDIR /cryptpad

COPY --from=build --chown=cryptpad:cryptpad /src /cryptpad
COPY --chown=cryptpad:cryptpad docker/cryptpad/docker-entrypoint.sh /usr/local/bin/cryptpad-entrypoint.sh
COPY --chown=cryptpad:cryptpad config/sso.js /cryptpad/config/sso.js

RUN chmod 0755 /usr/local/bin/cryptpad-entrypoint.sh \
    && mkdir -p /cryptpad/blob /cryptpad/block /cryptpad/customize /cryptpad/data /cryptpad/datastore \
    && chown -R cryptpad:cryptpad /cryptpad

USER cryptpad

EXPOSE 3000 3003

ENTRYPOINT ["/usr/local/bin/cryptpad-entrypoint.sh"]
CMD ["node", "server"]
