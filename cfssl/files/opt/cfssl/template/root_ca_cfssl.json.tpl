{{ $default_expiry := getenv "CFSSL_SIGN_DEFAULT_EXPIRY" "1008h" }}
{
  "signing": {
    "default": {
      "expiry": "{{ print $default_expiry }}",
      "ocsp_url": "https://{{ getenv "OCSP_HOST" "localmaeher.dev.pvarki.fi" }}:{{ getenv "OCSP_PORT" "4439" }}/ca/ocsp",
      "crl_url": "https://{{ getenv "OCSP_HOST" "localmaeher.dev.pvarki.fi" }}:{{ getenv "OCSP_PORT" "4439" }}/ca/crl/crl.pem"
    },
    "profiles": {
      "ocsp": {
        "usages": ["digital signature", "ocsp signing"],
        "expiry": "{{ getenv "CFSSL_SIGN_OCSP_EXPIRY" "2016h" }}"
      },
      "client": {
        "expiry": "{{ getenv "CFSSL_SIGN_CLIENT_EXPIRY" $default_expiry }}",
        "usages": [
          "signing",
          "digital signature",
          "key encipherment",
          "client auth"
        ]
      },
      "intermediate_ca": {
        "ca_constraint": {
          "is_ca": true,
          "max_path_len": 0,
          "max_path_len_zero": true
        },
        "expiry": "{{ getenv "CFSSL_SIGN_CA_EXPIRY" "2016h" }}",
        "usages": [
          "signing",
          "digital signature",
          "key encipherment",
          "cert sign",
          "crl sign",
          "server auth",
          "client auth"
        ]
      },
      "peer": {
        "expiry": "{{ getenv "CFSSL_SIGN_PEER_EXPIRY" $default_expiry }}",
        "usages": [
          "signing",
          "digital signature",
          "key encipherment",
          "client auth",
          "server auth"
        ]
      },
      "server": {
        "expiry": "{{ getenv "CFSSL_SIGN_SERVER_EXPIRY" $default_expiry }}",
        "usages": [
          "signing",
          "digital signing",
          "key encipherment",
          "server auth"
        ]
      }
    }
  }
}
