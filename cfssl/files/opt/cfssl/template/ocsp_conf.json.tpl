{
  "CN": "{{getenv "CFSSL_CA_NAME" "RASENMAEHER"}} OCSP",
  "key": {
    "algo": "rsa",
    "size": {{getenv "CFSSL_CA_KEYSIZE" "4096"}}
  },
  "names": [
    {
      "OU": "RASENMAEHER"
    }
  ]
}
