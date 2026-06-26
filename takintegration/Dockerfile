# syntax=docker/dockerfile:1.1.7-experimental
ARG TEMURIN_VERSION="17"
ARG TAKSERVER_IMAGE="pvarki/takserver:5.7-RELEASE-8"
ARG PYPI_INDEX_URL=https://pypi.org/simple

# The local reference tak_server is used in future stages
FROM ${TAKSERVER_IMAGE} as tak_server

#############################################
# Tox testsuite for multiple python version #
#############################################
FROM advian/tox-base:debian-bookworm as tox
ARG PYTHON_VERSIONS="3.11 3.12 3.13 3.14"
ARG UV_VERSION="0.11.6"
RUN export RESOLVED_VERSIONS=`pyenv_resolve $PYTHON_VERSIONS` \
    && echo RESOLVED_VERSIONS=$RESOLVED_VERSIONS \
    && for pyver in $RESOLVED_VERSIONS; do pyenv install -s $pyver; done \
    && pyenv global $RESOLVED_VERSIONS \
    && pip install -U "uv==$UV_VERSION" tox tox-uv \
    && apt-get update && apt-get install -y \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && true


######################
# Base builder image #
######################
FROM eclipse-temurin:${TEMURIN_VERSION}-noble as builder_base
#FROM python:3.11-bookworm as builder_base
COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /usr/local/bin/

ENV \
  # locale
  LC_ALL=C.UTF-8 \
  # python:
  PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  # pip:
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
#  PIP_INDEX_URL=https://nexus.dev.pvarki.fi/repository/python/simple \
  # uv:
#  UV_DEFAULT_INDEX=https://nexus.dev.pvarki.fi/repository/python/simple \
  UV_PROJECT_ENVIRONMENT=/.venv \
  UV_LINK_MODE=copy
RUN apt-get update && apt-get install -y \
        curl \
        git \
        bash \
        build-essential \
        libffi-dev \
        libssl-dev \
        libzmq3-dev \
        tini \
        openssh-client \
        cargo \
        python3 \
        python3-pip \
        python3-virtualenv  \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    # githublab ssh
    && mkdir -p -m 0700 ~/.ssh && ssh-keyscan gitlab.com github.com | sort > ~/.ssh/known_hosts \
    && true
RUN curl -fsSL https://deb.nodesource.com/setup_24.x | bash - \
    && apt-get install -y nodejs \
    && corepack enable \
    && corepack prepare pnpm@11.1.0 --activate
SHELL ["/bin/bash", "-lc"]
# Copy only requirements, to cache them in docker layer:
WORKDIR /pysetup
COPY ./uv.lock ./pyproject.toml ./README.rst /pysetup/
# Cache and install runtime deps into the project venv (without installing the project itself yet)
RUN --mount=type=ssh uv venv /.venv \
    && echo 'source /.venv/bin/activate' >>/root/.profile \
    && uv export --frozen --no-dev --format requirements.txt --no-hashes --output-file  /tmp/requirements.txt \
    && pip3 wheel --extra-index-url https://nexus.dev.pvarki.fi/repository/python/simple --wheel-dir=/tmp/wheelhouse -r /tmp/requirements.txt \
    && true


####################################
# Base stage for production builds #
####################################
FROM builder_base as production_build
# Copy entrypoint script
COPY ./docker/entrypoint.sh /docker-entrypoint.sh
COPY --from=builder_base /tmp/wheelhouse /tmp/wheelhouse
# Only files needed by production setup
COPY ./uv.lock ./pyproject.toml ./README.rst /app/
COPY ./src /app/src/
COPY ./ui /ui/
WORKDIR /ui
RUN CI=true pnpm install --frozen-lockfile && pnpm build
RUN mkdir -p /ui_build && cp -r dist/* /ui_build/
WORKDIR /app
# Build the wheel package with uv
RUN --mount=type=ssh source /.venv/bin/activate \
    && mkdir -p /tmp/wheelhouse \
    && uv build --wheel --out-dir /tmp/wheelhouse \
    && chmod a+x /docker-entrypoint.sh \
    && true


#########################
# Main production build #
#########################
FROM eclipse-temurin:${TEMURIN_VERSION}-noble as production
ARG PYPI_INDEX_URL
COPY --from=production_build /tmp/wheelhouse /tmp/wheelhouse
COPY --from=production_build /ui_build /ui_build
COPY --from=production_build /docker-entrypoint.sh /docker-entrypoint.sh
COPY --from=pvarki/kw_product_init:latest /kw_product_init /kw_product_init
# FIXME: Figure out exactly which jars we need and copy only those
COPY --from=tak_server /opt/tak /opt/tak
COPY --from=tak_server /opt/scripts /opt/scripts
COPY --from=tak_server /opt/templates /opt/templates
COPY docker/container-init.sh /container-init.sh

WORKDIR /app
# Install system level deps for running the package (not devel versions for building wheels)
# and install the wheels we built in the previous step. generate default config
RUN --mount=type=ssh apt-get update && apt-get install -y \
        bash \
        libffi8 \
        tini \
        git \
        openssh-client \
        curl \
        jq \
        python3 \
        python3-pip \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && chmod a+x /docker-entrypoint.sh \
    && WHEELFILE=`echo /tmp/wheelhouse/takrmapi-*.whl` \
    && pip3 install --break-system-packages --find-links=/tmp/wheelhouse/ "$WHEELFILE" \
    && rm -rf /tmp/wheelhouse/ \
    # Make some directories
    && mkdir -p /opt/tak/data/certs \
    # Get tool for waiting for ports
    && curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/bin/wait-for-it.sh \
    && chmod a+x /usr/bin/wait-for-it.sh \
    && true
ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]


#####################################
# Base stage for development builds #
#####################################
FROM builder_base as devel_build
# Install deps
COPY . /app
WORKDIR /app/ui
RUN CI=true pnpm install --frozen-lockfile && pnpm build
WORKDIR /app
RUN --mount=type=ssh source /.venv/bin/activate \
    && uv sync --frozen \
    && true


#0############
# Run tests #
#############
FROM devel_build as test
WORKDIR /app/ui
RUN mkdir -p /ui_build && cp -r dist/* /ui_build/
WORKDIR /app
ENTRYPOINT ["/usr/bin/tini", "--", "docker/entrypoint-test.sh"]
# Re run install to get the service itself installed
RUN --mount=type=ssh source /.venv/bin/activate \
    && uv sync --frozen \
    && ln -s /app/docker/container-init.sh /container-init.sh \
    && SKIP="uv-lock" docker/pre_commit_init.sh \
    && true


###########
# Hacking #
###########
FROM devel_build as devel_shell
# Copy everything to the image
WORKDIR /app/ui
COPY --from=pvarki/kw_product_init:latest /kw_product_init /kw_product_init
RUN mkdir -p /ui_build && cp -r dist/* /ui_build/
WORKDIR /app
RUN apt-get update && apt-get install -y zsh \
    && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
    && echo "source /root/.profile" >>/root/.zshrc \
    && pip3 install --break-system-packages git-up \
    && ln -s /app/docker/container-init.sh /container-init.sh \
    && curl https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh -o /usr/bin/wait-for-it.sh \
    && chmod a+x /usr/bin/wait-for-it.sh \
    && true
ENTRYPOINT ["/bin/zsh", "-l"]


############################
# Compose container target #
############################
FROM devel_shell as integ_devel_shell
COPY --from=tak_server /opt/tak /opt/tak
COPY --from=tak_server /opt/scripts /opt/scripts
COPY --from=tak_server /opt/templates /opt/templates
