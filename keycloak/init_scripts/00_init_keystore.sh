#!/usr/bin/env -S /bin/bash
KCI_SERVER_KEY_FILENAME="${KCI_SERVER_KEY_FILENAME:-/le_certs/rasenmaeher/privkey.pem}"
KCI_SERVER_CERT_FILENAME="${KCI_SERVER_CERT_FILENAME:-/le_certs/rasenmaeher/fullchain.pem}"
DATADIR="/opt/keycloak/data"

pushd $DATADIR >> /dev/null

openssl list -providers 2>&1 | grep "\(invalid command\|unknown option\)" >/dev/null
if [ $? -ne 0 ] ; then
  echo "Using legacy provider"
  LEGACY_PROVIDER="-legacy"
fi


echo "(re)Add TLS keys to keystore"
# We have to do this pkcs12 song and dance because keytool can't import private keys directly
# Create kcserver.p12 using certificates from RM
openssl pkcs12 ${LEGACY_PROVIDER} -export -out kcserver.p12 \
  -inkey "${KCI_SERVER_KEY_FILENAME}" \
  -in "${KCI_SERVER_CERT_FILENAME}" \
  -name "${KCI_SERVER_HOSTNAME}" \
  -passout pass:${KC_HTTPS_KEY_STORE_PASSWORD}

# Remove the old key (if exists)
echo "LE server cert & key"
keytool -delete \
  -alias "${KCI_SERVER_HOSTNAME}" \
  -keystore kcserver-keys.jks \
  -storepass "${KC_HTTPS_KEY_STORE_PASSWORD}"
# Create the Java keystore and import kcserver.p12
keytool -importkeystore -srcstoretype PKCS12 \
  -destkeystore kcserver-keys.jks \
  -srckeystore kcserver.p12 \
  -alias "${KCI_SERVER_HOSTNAME}" \
  -srcstorepass "${KC_HTTPS_KEY_STORE_PASSWORD}" \
  -deststorepass "${KC_HTTPS_KEY_STORE_PASSWORD}" \
  -destkeypass "${KC_HTTPS_KEY_STORE_PASSWORD}"

# Put the CA certs one-by-one (can't import full chains in one go) to the truststore
# Remove the old root key (if exists)
echo "RM root"
keytool -delete \
  -alias "RM_Root" \
  -keystore kcserver-truststore.jks \
  -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}
# Add root key
keytool -noprompt -import -trustcacerts \
  -file "/ca_public/root_ca.pem" \
  -alias "RM_Root" \
  -keystore kcserver-truststore.jks \
  -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}

# Remove the old intermediate key (if exists)
echo "RM intermediate"
keytool -delete \
  -alias "RM_Intermediate" \
  -keystore kcserver-truststore.jks \
  -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}
# Add intermediate key
keytool -noprompt -import -trustcacerts \
  -file "/ca_public/intermediate_ca.pem" \
  -alias "RM_Intermediate" \
  -keystore kcserver-truststore.jks \
  -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}

if [[ -f "/ca_public/miniwerk_ca.pem" ]];then
  # Remove the old key (if exists)
  echo "MiniWerk root cert"
  keytool -delete \
    -alias "MW_Root" \
    -keystore kcserver-truststore.jks \
    -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}
  keytool -noprompt -import -trustcacerts \
    -file /ca_public/miniwerk_ca.pem \
    -alias "MW_Root" \
    -keystore kcserver-truststore.jks \
    -storepass ${KC_HTTPS_TRUST_STORE_PASSWORD}
fi

popd
