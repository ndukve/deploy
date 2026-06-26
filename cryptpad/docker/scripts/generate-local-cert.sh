#!/bin/sh
set -eu

CERT_DIR="${CERT_DIR:-/etc/nginx/certs}"
CERT_FILE="${CERT_DIR}/cryptpad.local.pem"
KEY_FILE="${CERT_DIR}/cryptpad.local-key.pem"
MAIN_HOST="${CRYPTPAD_MAIN_HOST:-cryptpad.localhost}"
SANDBOX_HOST="${CRYPTPAD_SANDBOX_HOST:-sandbox.cryptpad.localhost}"
RM_HOST="${CRYPTPAD_RM_HOST:-rmcryptpad.localhost}"

mkdir -p "$CERT_DIR"

if [ -s "$CERT_FILE" ] && [ -s "$KEY_FILE" ]; then
  exit 0
fi

umask 077

cat > /tmp/openssl.cnf <<EOF
[req]
distinguished_name = req_distinguished_name
x509_extensions = v3_req
prompt = no

[req_distinguished_name]
CN = ${MAIN_HOST}

[v3_req]
subjectAltName = @alt_names
keyUsage = digitalSignature, keyEncipherment
extendedKeyUsage = serverAuth

[alt_names]
DNS.1 = ${MAIN_HOST}
DNS.2 = ${SANDBOX_HOST}
DNS.3 = ${RM_HOST}
EOF

openssl req \
  -x509 \
  -newkey rsa:2048 \
  -sha256 \
  -nodes \
  -days 3650 \
  -keyout "$KEY_FILE" \
  -out "$CERT_FILE" \
  -config /tmp/openssl.cnf

chmod 0644 "$CERT_FILE"
