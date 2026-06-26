const baseConfig = require('./config.example.js');

const mainOrigin = process.env.CPAD_MAIN_DOMAIN || 'https://cryptpad.localhost:8443';
const sandboxOrigin =
  process.env.CPAD_SANDBOX_DOMAIN || 'https://sandbox.cryptpad.localhost:8443';

module.exports = {
  ...baseConfig,
  httpUnsafeOrigin: mainOrigin,
  httpSafeOrigin: sandboxOrigin,
  httpAddress: '0.0.0.0',
  httpPort: 3000,
  websocketPort: 3003,
  adminKeys: [],
  filePath: '/cryptpad/datastore/',
  archivePath: '/cryptpad/data/archive',
  pinPath: '/cryptpad/data/pins',
  taskPath: '/cryptpad/data/tasks',
  blockPath: '/cryptpad/block',
  blobPath: '/cryptpad/blob',
  blobStagingPath: '/cryptpad/data/blobstage',
  decreePath: '/cryptpad/data/decrees',
  logPath: false,
  logToStdout: true,
  installMethod: 'docker',
};
