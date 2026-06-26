ARG OPENLDAP_VERSION_TAG=2.5.14

FROM docker.io/bitnamilegacy/openldap:$OPENLDAP_VERSION_TAG AS production

# Adds custom libopenldap.sh that:
# 1. Properly disables anonymous access
# 2. Adds memberof-support to openLDAP
# 3. Set default custom tree.ldif (if it needs to be customized we need to update the /opt/bitnami/scripts/openldap/entrypoint.s script)
COPY ./rootfs /
