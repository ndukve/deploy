#!/bin/bash
# Add our CA to the main cacerts store
if [[ -f "/ca_public/miniwerk_ca.pem" ]];then
  echo "MiniWerk root to system CAs"
  keytool -delete -cacerts \
    -alias "MW_Root" \
    -storepass "changeit"
  keytool -noprompt -import -trustcacerts -cacerts \
    -file /ca_public/miniwerk_ca.pem \
    -alias "MW_Root" \
    -storepass "changeit"
fi

# Remove the old root key (if exists)
echo "RM root"
keytool -delete -cacerts \
  -alias "RM_Root" \
  -storepass "changeit"
# Add root key
keytool -noprompt -import -trustcacerts -cacerts \
  -file "/ca_public/root_ca.pem" \
  -alias "RM_Root" \
  -storepass "changeit"

# Remove the old intermediate key (if exists)
echo "RM intermediate"
keytool -delete -cacerts \
  -alias "RM_Intermediate" \
  -storepass "changeit"
# Add intermediate key
keytool -noprompt -import -trustcacerts -cacerts \
  -file "/ca_public/intermediate_ca.pem" \
  -alias "RM_Intermediate" \
  -storepass "changeit"
