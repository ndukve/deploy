import { useTranslation } from "react-i18next";

export const IosDownload = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="flex justify-center">
      <a
        href="https://apps.apple.com/us/app/itak/id1561656396"
        target="_blank"
        rel="noopener noreferrer"
        className="group inline-flex flex-col items-center gap-2 focus:outline-none"
      >
        <img
          src="/ui/tak/download-buttons/ios/app-store-badge.svg"
          width={150}
          className="rounded-md cursor-pointer transition-all
                    group-hover:scale-105
                    group-hover:shadow-lg
                    focus-visible:ring-2
                    focus-visible:ring-primary-light"
        />

        <span className="text-sm font-medium text-primary-light group-hover:underline">
          {t("onboarding.ios.downloadFromAppStore") ||
            "Download from App Store"}
        </span>
      </a>
    </div>
  );
};
