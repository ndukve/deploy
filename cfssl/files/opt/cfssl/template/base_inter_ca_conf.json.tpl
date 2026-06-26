{
  "CN": "{{getenv "CFSSL_CA_NAME" "RASENMAEHER"}}",
  "ca": {
    "expiry": "{{ getenv "CFSSL_CA_EXPIRY" "2016h" }}"
  },
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
