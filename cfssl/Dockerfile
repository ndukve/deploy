FROM cfssl/cfssl AS cfssl
ENV DEBIAN_FRONTEND=noninteractive

COPY ./files/docker-entrypoint.sh /docker-entrypoint.sh
COPY ./files/container-env.sh /container-env.sh
RUN apt-get update && apt-get install -y \
      tini \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && true
ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]

FROM cfssl AS base
RUN echo "deb http://deb.debian.org/debian bookworm-backports main" >/etc/apt/sources.list.d/backports.list \
    && apt-get update && apt-get install -y \
      jq \
      curl \
#    && /usr/bin/go install github.com/pressly/goose/v3/cmd/goose@v3.17.0 \  # using this needs a lot of changes to the migrations \
    && apt-get install -y -t bookworm-backports golang \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && /usr/bin/go install github.com/pressly/goose/v3/cmd/goose@v3.17.0 \
    && mkdir -p /opt/cfssl/persistent/certdb/sqlite/migrations \
    && true
CMD []
SHELL ["/bin/bash", "-lc"]


FROM debian:bookworm-slim AS production
COPY --from=hairyhenderson/gomplate:stable /gomplate /bin/gomplate
COPY ./files/opt/cfssl /opt/cfssl
COPY ./files/docker-entrypoint.sh /docker-entrypoint.sh
COPY ./files/container-env.sh /container-env.sh
COPY ./files/cfssl-init.sh /cfssl-init.sh
COPY ./files/cfssl-start.sh /cfssl-start.sh
COPY ./files/ocsp-start.sh /ocsp-start.sh
COPY --from=base /go/bin/goose /usr/bin/goose
COPY --from=base /usr/bin/cfssl /usr/bin/cfssl
COPY --from=base /usr/bin/cfssl-bundle /usr/bin/cfssl-bundle
COPY --from=base /usr/bin/cfssl-certinfo /usr/bin/cfssl-certinfo
COPY --from=base /usr/bin/cfssl-newkey /usr/bin/cfssl-newkey
COPY --from=base /usr/bin/cfssl-scan /usr/bin/cfssl-scan
COPY --from=base /usr/bin/cfssljson /usr/bin/cfssljson
WORKDIR /opt/cfssl
RUN apt-get update && apt-get install -y \
      jq \
      tini \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && true


FROM production AS api
ENV CFSSL_MODE=api
ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]

FROM production AS ocsp
ENV CFSSL_MODE=ocsp
ENTRYPOINT ["/usr/bin/tini", "--", "/docker-entrypoint.sh"]


FROM production AS python_base
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
  PIP_DEFAULT_TIMEOUT=100
SHELL ["/bin/bash", "-lc"]

COPY --from=ghcr.io/astral-sh/uv:0.11.6 /uv /uvx /bin/

RUN apt-get update \
    && apt-get install -y \
      python3-pip \
      curl \
      jq \
      python3-virtualenv \
      python3-wheel \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && true

# Copy only requirements, to cache them in docker layer:
WORKDIR /pysetup
COPY ./uv.lock ./pyproject.toml ./README.rst /pysetup/
# Install basic requirements (utilizing an internal docker wheelhouse if available)
RUN uv export --frozen --no-dev --no-emit-project --no-hashes --format requirements-txt -o /tmp/requirements.txt \
    && pip3 wheel --wheel-dir=/tmp/wheelhouse --extra-index-url https://nexus.dev.pvarki.fi/repository/pypilocal/simple/ -r /tmp/requirements.txt \
    && virtualenv /.venv && . /.venv/bin/activate && echo '. /.venv/bin/activate' >>/root/.profile \
    && pip3 install --no-deps --find-links=/tmp/wheelhouse/ /tmp/wheelhouse/*.whl \
    && true

#####################################
# Base stage for python prod builds #
#####################################
FROM python_base AS python_production_build
# Only files needed by production setup
COPY ./uv.lock ./pyproject.toml ./README.rst ./src /app/
WORKDIR /app
# Build the wheel package with uv and add it to the wheelhouse
RUN source /.venv/bin/activate \
    # wtf docker copy ??
    && mkdir src && mv ocsprest src/ \
    && uv build --wheel \
    && cp dist/*.whl /tmp/wheelhouse \
    && true

##############################################
# Main production build for the python thing #
##############################################
FROM production AS ocsprest
COPY --from=python_production_build /tmp/wheelhouse /tmp/wheelhouse
WORKDIR /app
# Install system level deps for running the package (not devel versions for building wheels)
# and install the wheels we built in the previous step. generate default config
RUN apt-get update && apt-get install -y \
        python3-pip \
        jq \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/* \
    && WHEELFILE=`echo /tmp/wheelhouse/ocsprest-*.whl` \
    && pip3 install --break-system-packages --find-links=/tmp/wheelhouse/ "$WHEELFILE"[all] \
    && rm -rf /tmp/wheelhouse/ \
    # Do whatever else you need to
    && true
COPY ./files/ocsprest-entrypoint.sh /ocsprest-entrypoint.sh
ENTRYPOINT ["/usr/bin/tini", "--", "/ocsprest-entrypoint.sh"]


###########
# Hacking #
###########
FROM python_base AS devel_shell
WORKDIR /app
RUN apt-get update && apt-get install -y zsh jq git vim \
    && sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" \
    && echo "source /root/.profile" >>/root/.zshrc \
    && pip3 install --break-system-packages git-up \
    && true
ENTRYPOINT ["/bin/zsh", "-l"]
