#!/usr/bin/env -S /bin/bash
set -euo pipefail

TR=/opt/tak

TAK_SERVER_KEY_FILENAME="${TAK_SERVER_KEY_FILENAME:-/le_certs/rasenmaeher/privkey.pem}"
TAK_SERVER_CERT_FILENAME="${TAK_SERVER_CERT_FILENAME:-/le_certs/rasenmaeher/fullchain.pem}"
TAKSERVER_KEYSTORE_PASS="${TAKSERVER_KEYSTORE_PASS:-takservercertpass}"
KEYSTORE_PASS="${KEYSTORE_PASS:-takcacertpw}"

# ── Wait for miniwerk to write certs and kraftwerk-init.json ──────────────────
echo "Waiting for kraftwerk-init.json..."
WAIT=0
until [ -f /pvarki/kraftwerk-init.json ]; do
    sleep 5; WAIT=$((WAIT+5))
    [ $WAIT -ge 300 ] && { echo "ERROR: /pvarki/kraftwerk-init.json not found after 5 min"; exit 1; }
done

echo "Waiting for LE certs..."
WAIT=0
until [ -f "${TAK_SERVER_CERT_FILENAME}" ] && [ -f "${TAK_SERVER_KEY_FILENAME}" ]; do
    sleep 5; WAIT=$((WAIT+5))
    [ $WAIT -ge 300 ] && { echo "ERROR: LE certs not found after 5 min (${TAK_SERVER_CERT_FILENAME})"; exit 1; }
done

echo "Waiting for CA certs..."
WAIT=0
until [ -f /ca_public/root_ca.pem ] && [ -f /ca_public/intermediate_ca.pem ]; do
    sleep 5; WAIT=$((WAIT+5))
    [ $WAIT -ge 300 ] && { echo "ERROR: CA certs not found after 5 min"; exit 1; }
done

TAK_SERVER_HOSTNAME="$(jq -r .product.dns /pvarki/kraftwerk-init.json)"
[ -z "${TAK_SERVER_HOSTNAME}" ] || [ "${TAK_SERVER_HOSTNAME}" = "null" ] && \
    { echo "ERROR: .product.dns missing from kraftwerk-init.json"; exit 1; }
echo "TAK hostname: ${TAK_SERVER_HOSTNAME}"

# ── Directory/symlink setup ───────────────────────────────────────────────────
mkdir -p "${TR}/data/logs" "${TR}/data/certs"

if [[ ! -L "${TR}/logs" ]]; then
    mv "${TR}/logs" "${TR}/logs.orig" 2>/dev/null || true
    ln -fs "${TR}/data/logs/" "${TR}/logs"
fi

if [[ ! -L "${TR}/certs" ]]; then
    mv "${TR}/certs" "${TR}/certs.orig" 2>/dev/null || true
    ln -fs "${TR}/data/certs/" "${TR}/certs"
fi

mkdir -p /opt/tak/data/certs/files
pushd /opt/tak/data/certs/files > /dev/null

# ── Detect legacy OpenSSL provider ───────────────────────────────────────────
LEGACY_PROVIDER=""
if openssl list -providers 2>&1 | grep -q "\(invalid command\|unknown option\)"; then
    echo "Using legacy provider"
    LEGACY_PROVIDER="-legacy"
fi

# ── Build TLS keystore from LE/mkcert cert ────────────────────────────────────
echo "(re)Add TLS keys to keystore"

openssl pkcs12 ${LEGACY_PROVIDER} -export \
    -out takserver.p12 \
    -inkey "${TAK_SERVER_KEY_FILENAME}" \
    -in "${TAK_SERVER_CERT_FILENAME}" \
    -name "${TAK_SERVER_HOSTNAME}" \
    -passout pass:${TAKSERVER_KEYSTORE_PASS}

# Delete old alias (ok if it doesn't exist yet)
keytool -delete -alias "${TAK_SERVER_HOSTNAME}" \
    -keystore takserver.jks \
    -storepass "${TAKSERVER_KEYSTORE_PASS}" 2>/dev/null || true

keytool -importkeystore -srcstoretype PKCS12 \
    -destkeystore takserver.jks \
    -srckeystore takserver.p12 \
    -alias "${TAK_SERVER_HOSTNAME}" \
    -srcstorepass "${TAKSERVER_KEYSTORE_PASS}" \
    -deststorepass "${TAKSERVER_KEYSTORE_PASS}" \
    -destkeypass "${TAKSERVER_KEYSTORE_PASS}" \
    -noprompt

# ── Build truststore from RASENMAEHER CA chain ────────────────────────────────
keytool -delete -alias "RM_Root" \
    -keystore takserver-truststore.jks \
    -storepass "${KEYSTORE_PASS}" 2>/dev/null || true

keytool -noprompt -import -trustcacerts \
    -file "/ca_public/root_ca.pem" \
    -alias "RM_Root" \
    -keystore takserver-truststore.jks \
    -storepass "${KEYSTORE_PASS}"

keytool -delete -alias "RM_Intermediate" \
    -keystore takserver-truststore.jks \
    -storepass "${KEYSTORE_PASS}" 2>/dev/null || true

keytool -noprompt -import -trustcacerts \
    -file "/ca_public/intermediate_ca.pem" \
    -alias "RM_Intermediate" \
    -keystore takserver-truststore.jks \
    -storepass "${KEYSTORE_PASS}"

if [[ -f "/ca_public/miniwerk_ca.pem" ]]; then
    keytool -delete -alias "MW_Root" \
        -keystore takserver-truststore.jks \
        -storepass "${KEYSTORE_PASS}" 2>/dev/null || true

    keytool -noprompt -import -trustcacerts \
        -file /ca_public/miniwerk_ca.pem \
        -alias "MW_Root" \
        -keystore takserver-truststore.jks \
        -storepass "${KEYSTORE_PASS}"
fi

cp -v takserver-truststore.jks fed-truststore.jks
cp -v takserver-truststore.jks truststore-root.jks

popd > /dev/null
echo "Keystores built successfully"

# ── First-run DB init (skipped on subsequent starts) ─────────────────────────
if [ -f /opt/tak/data/firstrun.done ]; then
    echo "First run already done, skipping DB import"
    exit 0
fi

echo "Waiting for postgres..."
WAITFORIT_TIMEOUT=120 /usr/bin/wait-for-it.sh "${POSTGRES_ADDRESS}:5432" -- true

echo "Init DB"
PGPASSWORD="${POSTGRES_PASSWORD}" psql -v ON_ERROR_STOP=1 \
    -h "${POSTGRES_ADDRESS}" -U "${POSTGRES_USER}" "${POSTGRES_DB}" \
    --single-transaction --file /opt/scripts/takdb_base.sql

java -jar "${TR}/db-utils/SchemaManager.jar" \
    -url "jdbc:postgresql://${POSTGRES_ADDRESS}:5432/${POSTGRES_DB}" \
    -user "${POSTGRES_USER}" \
    -password "${POSTGRES_PASSWORD}" \
    upgrade

date -u +"%Y%m%dT%H%M" > /opt/tak/data/firstrun.done
echo "TAK first-run init complete"
