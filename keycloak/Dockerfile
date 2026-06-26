ARG KC_VERSION_TAG=24.0.5

# Install some packages we need https://www.keycloak.org/server/containers#_installing_additional_rpm_packages
FROM registry.access.redhat.com/ubi9 AS ubi-micro-build
RUN mkdir -p /mnt/rootfs
RUN dnf install --installroot /mnt/rootfs  \
      openssl \
      gawk \
      sed \
      curl \
      --releasever 9 --setopt install_weak_deps=false --nodocs -y && \
    dnf --installroot /mnt/rootfs clean all && \
    rpm --root /mnt/rootfs -e --nodeps setup

FROM keycloak/keycloak:$KC_VERSION_TAG AS builder
ARG KC_DB_VENDOR=postgres
ARG KC_CACHE=ispn
RUN /opt/keycloak/bin/kc.sh build \
      --db="${KC_DB_VENDOR}" \
      --cache="${KC_CACHE}" \
      --health-enabled=true \
      --https-client-auth=request

FROM keycloak/keycloak:$KC_VERSION_TAG AS production
ENV QUARKUS_TRANSACTION_MANAGER_ENABLE_RECOVERY=true \
    KC_HEALTH_ENABLED=true
COPY --from=builder /opt/keycloak/ /opt/keycloak/
COPY --from=ubi-micro-build /mnt/rootfs /
COPY custom_entrypoint.sh /custom_entrypoint.sh
ENTRYPOINT ["/custom_entrypoint.sh"]
