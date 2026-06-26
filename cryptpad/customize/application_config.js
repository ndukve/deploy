(() => {
  const factory = (AppConfig) => {
    AppConfig.loginSalt = '__LOGIN_SALT__'; // replaced at container startup
    AppConfig.minimumPasswordLength = 8;
    AppConfig.defaultDarkTheme = 'true';

    // Hide donation/crowdfunding prompts
    AppConfig.disableFeedback = true;

    // Hide footer links that don't apply to a private deployment
    AppConfig.source = false;
    AppConfig.roadmap = false;

    return AppConfig;
  };

  if (typeof module !== 'undefined' && module.exports) {
    module.exports = factory(require('../www/common/application_config_internal.js'));
  } else if (typeof define !== 'undefined' && define !== null && define.amd !== null) {
    define(['/common/application_config_internal.js'], factory);
  }
})();
