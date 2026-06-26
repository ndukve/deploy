module.exports = {
  enabled: true,
  enforced: true,
  cpPassword: false,
  forceCpPassword: false,
  list: [
    {
      name: process.env.CPAD_SSO_NAME || 'rmcryptpad',
      type: 'oidc',
      url:
        process.env.CPAD_SSO_DISCOVERY_URL ||
        process.env.CPAD_SSO_ISSUER ||
        'https://rmcryptpad.localhost:8443',
      client_id: process.env.CPAD_SSO_CLIENT_ID || 'cryptpad',
      client_secret: process.env.CPAD_SSO_CLIENT_SECRET || 'change-me',
      username_claim: 'preferred_username',
      id_token_alg: 'RS256',
      use_pkce: true,
      use_nonce: true,
    },
  ],
};
