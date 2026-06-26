#!/usr/bin/env -S /bin/bash
set -e

. /container-env.sh
#
# Run certificate init procedures if the CA file doesn't exists
#
if [[ ! -f "${RUN_CA}" ]]
then
    echo "$(date) --- Init CA certificates"
    mkdir -p "${CFSSL_PERSISTENT_FOLDER}"

    # Check the CA config source. It's either json string or file and copy it to place
    if [ "$INIT_CA_JSON_STRING" != "NA" ]
    then
        echo "$(date) --- Using INIT_CA_JSON_STRING variables as base config"
        if echo $INIT_CA_JSON_STRING | jq > /dev/null
        then
            echo "${INIT_CA_JSON_STRING}" > "$RUN_CA_CONF"
        else
            echo $INIT_CA_JSON_STRING | jq
            echo "$(date) --- ERROR - INIT_CA_JSON_STRING is not valid JSON"
            exit
        fi
    else
        if [[ -f "$INIT_CA_JSON_FILE" ]]
        echo "$(date) --- Using file defined in INIT_CA_JSON_FILE as base config"
        then
            if gomplate -f "$INIT_CA_JSON_FILE" | jq > /dev/null
            then
                gomplate -f "$INIT_CA_JSON_FILE" | jq > "$RUN_CA_CONF"
            else
                gomplate -f "$INIT_CA_JSON_FILE" | jq
                echo "$(date) --- ERROR - INIT_CA_JSON_FILE doesnt contain valid JSON"
                exit
            fi
        else
            echo "$(date) --- ERROR - INIT_CA_JSON_FILE not found"
            exit
        fi
    fi

    # Check the INTER CA config source. It's either json string or file and copy it to place
    if [ "$INIT_INTER_CA_JSON_STRING" != "NA" ]
    then
        echo "$(date) --- Using INIT_INTER_CA_JSON_STRING variables as base config"
        if echo $INIT_INTER_CA_JSON_STRING | jq > /dev/null
        then
            echo "${INIT_INTER_CA_JSON_STRING}" > "$RUN_INTER_CA_CONF"
        else
            echo $INIT_INTER_CA_JSON_STRING | jq
            echo "$(date) --- ERROR - INIT_INTER_CA_JSON_STRING is not valid JSON"
            exit
        fi

    else
        echo "$(date) --- Using file defined in INIT_CA_JSON_FILE as base config"
        if gomplate -f  "$INIT_INTER_CA_JSON_FILE" | jq > /dev/null
        then
            gomplate -f "$INIT_INTER_CA_JSON_FILE" | jq > "$RUN_INTER_CA_CONF"
        else
            gomplate -f "$INIT_INTER_CA_JSON_FILE" | jq
            echo "$(date) --- ERROR - INIT_INTER_CA_JSON_FILE doesnt contain valid JSON"
            exit
        fi
    fi


    if gomplate -f "$INIT_CA_CONFIG_JSON_FILE" | jq > /dev/null
    then
        gomplate -f "$INIT_CA_CONFIG_JSON_FILE" | jq > "$RUN_CA_CFSSL_CONF"
    else
        gomplate -f "$INIT_CA_CONFIG_JSON_FILE" | jq
        echo "$(date) --- ERROR - INIT_CA_CONFIG_JSON_FILE doesnt contain valid JSON"
        exit
    fi

    # Check the OCSP config source. It's either json string or file and copy it to place
    if [ "$INIT_OCSP_JSON_STRING" != "NA" ]
    then
        echo "$(date) --- Using INIT_INTER_CA_JSON_STRING variables as base config"
        if echo $INIT_OCSP_JSON_STRING | jq > /dev/null
        then
            echo "${INIT_OCSP_JSON_STRING}" > "$RUN_OCSP_CONF"
        else
            echo $INIT_OCSP_JSON_STRING | jq
            echo "$(date) --- ERROR - INIT_OCSP_JSON_STRING is not valid JSON"
            exit
        fi

    else
        echo "$(date) --- Using file defined in INIT_OCSP_JSON_FILE as base config"
        if gomplate -f  "$INIT_OCSP_JSON_FILE" | jq > /dev/null
        then
            gomplate -f "$INIT_OCSP_JSON_FILE" | jq > "$RUN_OCSP_CONF"
        else
            gomplate -f "$INIT_OCSP_JSON_FILE" | jq
            echo "$(date) --- ERROR - INIT_OCSP_JSON_FILE doesnt contain valid JSON"
            exit
        fi
    fi



    # Generate new CA files
    pushd "${CFSSL_PERSISTENT_FOLDER}" > /dev/null
    cfssl gencert -initca "${RUN_CA_CONF}" | cfssljson -bare init_ca

    cfssl gencert -initca "${RUN_INTER_CA_CONF}" | cfssljson -bare init_intermediate_ca
    cfssl sign -ca init_ca.pem -ca-key init_ca-key.pem -config "${RUN_CA_CFSSL_CONF}" -profile intermediate_ca init_intermediate_ca.csr | cfssljson -bare init_intermediate_ca

    # Generate OSCP certs
    cfssl gencert -ca init_intermediate_ca.pem -ca-key init_intermediate_ca-key.pem -config "${RUN_CA_CFSSL_CONF}" -profile="ocsp" "$RUN_OCSP_CONF" | cfssljson -bare server-ocsp -

    # Copy temporary CA files to persistent path
    cp init_ca.pem "${RUN_CA}"
    cp init_ca-key.pem "${RUN_INTER_CA_KEY}"
    cp init_intermediate_ca.pem "${RUN_INTER_CA}"
    cp init_intermediate_ca-key.pem "${RUN_INTER_CA_KEY}"
    cp server-ocsp.pem "${RUN_OCSP_CERT}"
    cp server-ocsp-key.pem "${RUN_OCSP_KEY}"

    popd > /dev/null
    echo "$(date) --- Init complete..."

fi


#
# Run goose init (copy files), use alternative files if one is defined in env vars...
#
if [[ ! -f "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations/001_CreateCertificates.sql" ]]
then
    echo "$(date) --- running first time goose init tasks..."
    mkdir -p "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations"

    if [ "$INIT_GOOSE_DBJSON_FILE" != "NA" ]
    then
        cp "${INIT_GOOSE_DBJSON_FILE}" "${CFSSL_PERSISTENT_FOLDER}/db.json"
    else
        cp "/opt/cfssl/template/goose/db.json" "${CFSSL_PERSISTENT_FOLDER}/db.json"
    fi

    if [ "${INIT_GOOSE_CREATECERTIFICATES_SQL_FILE}" != "NA" ]
    then
        cp "${INIT_GOOSE_CREATECERTIFICATES_SQL_FILE}" "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations/001_CreateCertificates.sql"
    else
        cp "/opt/cfssl/template/goose/001_CreateCertificates.sql" "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations/001_CreateCertificates.sql"
    fi

    if [ "${INIT_GOOSE_ADDMETADATA_SQL_FILE}" != "NA" ]
    then
        cp "${INIT_GOOSE_ADDMETADATA_SQL_FILE}" "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations/002_AddMetadataToCertificates.sql"
    else
        cp "/opt/cfssl/template/goose/002_AddMetadataToCertificates.sql" "${CFSSL_PERSISTENT_FOLDER}/certdb/sqlite/migrations/002_AddMetadataToCertificates.sql"
    fi

fi

if [[ -d "${INT_SHARED_CERT_FOLDER}" ]]
then
    # Copy CA files to persistent path
    cat "${RUN_INTER_CA}" "${RUN_CA}" > "${INT_SHARED_CERT_FOLDER}/ca_chain.pem"
    cat "${RUN_INTER_CA}" > "${INT_SHARED_CERT_FOLDER}/intermediate_ca.pem"
    cat "${RUN_CA}" > "${INT_SHARED_CERT_FOLDER}/root_ca.pem"
fi
