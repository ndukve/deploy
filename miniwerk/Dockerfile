# syntax=docker/dockerfile:1.1.7-experimental
#############################################
# Tox testsuite for multiple python version #
#############################################
FROM advian/tox-base:debian-bookworm AS tox
ARG PYTHON_VERSIONS="3.11"
ARG UV_VERSION="0.11.6"
RUN export RESOLVED_VERSIONS=`pyenv_resolve $PYTHON_VERSIONS` \
    && echo RESOLVED_VERSIONS=$RESOLVED_VERSIONS \
    && for pyver in $RESOLVED_VERSIONS; do pyenv install -s $pyver; done \
    && pyenv global $RESOLVED_VERSIONS \
    && pip install -U "uv==$UV_VERSION" tox \
    && apt-get update && apt-get install -y \
        mkcert \
        git \
    && rm -rf /var/lib/apt/lists/* \
    && true

######################
# Base builder image #
######################
FROM python:3.14-trixie AS builder_base
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
  # uv:
  UV_PROJECT_ENVIRONMENT=/.venv \
  UV_LINK_MODE=copy


RUN apt-get update && apt-get install -y \
        curl \
        git \
        bash \
        build-essential \
        libffi-dev \
        libssl-dev \
        tini \
        openssh-client \
        cargo \
        jq \
        mkcert \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    # githublab ssh
    && mkdir -p -m 0700 ~/.ssh && ssh-keyscan gitlab.com github.com | sort > ~/.ssh/known_hosts \
    && true

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
FROM builder_base AS production_build
# Copy entrypoint script
COPY ./docker/entrypoint.sh /docker-entrypoint.sh
# Only files needed by production setup
COPY ./uv.lock ./pyproject.toml ./README.rst /app/
COPY ./src /app/src/
WORKDIR /app
COPY --from=builder_base /tmp/wheelhouse /tmp/wheelhouse
# Build the wheel package with uv
RUN --mount=type=ssh source /.venv/bin/activate \
    && mkdir -p /tmp/wheelhouse \
    && uv build --wheel --out-dir /tmp/wheelhouse \
    && chmod a+x /docker-entrypoint.sh \
    && true


#########################
# Main production build #
#########################
FROM python:3.14-slim-trixie AS production
COPY --from=production_build /tmp/wheelhouse /tmp/wheelhouse
COPY --from=production_build /docker-entrypoint.sh /docker-entrypoint.sh
WORKDIR /app
# Install system level deps for running the package (not devel versions for building wheels)
# and install the wheels we built in the previous step. generate default config
RUN --mount=type=ssh apt-get update && apt-get install -y \
        bash \
        libffi8 \
        tini \
        jq \
        mkcert \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && chmod a+x /docker-entrypoint.sh \
    && WHEELFILE=`echo /tmp/wheelhouse/miniwerk-*.whl` \
    && pip3 install --find-links=/tmp/wheelhouse/ "$WHEELFILE"[all] \
    && rm -rf /tmp/wheelhouse/ \
    # Do whatever else you need to
    && true
ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]


#####################################
# Base stage for development builds #
#####################################
FROM builder_base AS devel_build
# Install deps including dev group
WORKDIR /pysetup
RUN --mount=type=ssh source /.venv/bin/activate \
    && uv sync --frozen --no-install-project \
    && true


#0############
# Run tests #
#############
FROM devel_build AS test
COPY . /app
WORKDIR /app
ENTRYPOINT ["/usr/bin/tini", "--", "docker/entrypoint-test.sh"]
# Re run install to get the service itself installed
RUN --mount=type=ssh source /.venv/bin/activate \
    && uv sync --frozen \
    && docker/pre_commit_init.sh \
    && true


###########
# Hacking #
###########
FROM devel_build AS devel_shell
# Copy everything to the image
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y zsh \
    && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
    && echo "source /root/.profile" >>/root/.zshrc \
    && echo 'export MW_DATA_PATH="/app/devdata"' >>/root/.profile \
    && echo 'export CAROOT="/app/devdata/mkcert"' >>/root/.profile \
    && pip3 install git-up \
    && true
ENTRYPOINT ["/bin/zsh", "-l"]
