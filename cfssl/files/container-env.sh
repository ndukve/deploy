#!/usr/bin/env -S /bin/bash
set -e
CFSSL_BIND_ADDRESS="${CFSSL_BIND_ADDRESS:-0.0.0.0}"
CFSSL_BIND_PORT="${CFSSL_BIND_PORT:-8888}"
CFSSL_OCSP_BIND_PORT="${CFSSL_OCSP_BIND_PORT:-8889}"

# CA Cert key and config filen path
CFSSL_PERSISTENT_FOLDER="${CFSSL_PERSISTENT_FOLDER:-/data/persistent}"
RUN_DB_CONFIG="${RUN_DB_CONFIG:-/data/persistent/db.json}"
RUN_CA="${RUN_CA:-/data/persistent/ca.pem}"
RUN_CA_KEY="${RUN_CA_KEY:-/data/persistent/ca_key.pem}"
RUN_CA_CONF="${RUN_CA_CONF:-/data/persistent/ca_conf.json}"
RUN_CA_CFSSL_CONF="${RUN_CA_CFSSL_CONF:-/data/persistent/root_ca_cfssl.json}"

RUN_INTER_CA="${RUN_INTER_CA:-/data/persistent/inter-ca.pem}"
RUN_INTER_CA_KEY="${RUN_INTER_CA_KEY:-/data/persistent/inter-ca_key.pem}"
RUN_INTER_CA_CONF="${RUN_INTER_CA_CONF:-/data/persistent/inter-ca_conf.json}"

RUN_OCSP_CERT="${RUN_OCSP_CERT:-/data/persistent/ocsp.pem}"
RUN_OCSP_KEY="${RUN_OCSP_KEY:-/data/persistent/ocsp_key.pem}"
RUN_OCSP_CONF="${RUN_OCSP_CONF:-/data/persistent/ocsp_conf.json}"

# Root CA CSR config either in file or json string
# This configuration file contains "CSR" information.
INIT_CA_JSON_FILE="${INIT_CA_JSON_FILE:-/opt/cfssl/template/base_ca_conf.json.tpl}"
INIT_CA_JSON_STRING="${INIT_CA_JSON_STRING:-NA}"
# This configuration file contains "Certificate signing" information
INIT_CA_CONFIG_JSON_FILE="${INIT_CA_CONFIG_JSON_FILE:-/opt/cfssl/template/root_ca_cfssl.json.tpl}"

# Intermediate CA CSR configuration in file or json string
INIT_INTER_CA_JSON_FILE="${INIT_INTER_CA_JSON_FILE:-/opt/cfssl/template/base_inter_ca_conf.json.tpl}"
INIT_INTER_CA_JSON_STRING="${INIT_INTER_CA_JSON_STRING:-NA}"

# OCSP CSR configuration in file or json string
INIT_OCSP_JSON_FILE="${INIT_OCSP_JSON_FILE:-/opt/cfssl/template/ocsp_conf.json.tpl}"
INIT_OCSP_JSON_STRING="${INIT_OCSP_JSON_STRING:-NA}"


# Alternative goose init config files can be changed using these.
INIT_GOOSE_DBJSON_FILE="${INIT_GOOSE_DBJSON_FILE:-NA}"
INIT_GOOSE_CREATECERTIFICATES_SQL_FILE="${INIT_GOOSE_CREATECERTIFICATES_SQL_FILE:-NA}"
INIT_GOOSE_ADDMETADATA_SQL_FILE="${INIT_GOOSE_ADDMETADATA_SQL_FILE:-NA}"

INT_SHARED_CERT_FOLDER="${INT_SHARED_CERT_FOLDER:-/ca_public}"
