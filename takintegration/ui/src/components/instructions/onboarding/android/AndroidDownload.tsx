import { useTranslation } from "react-i18next";

export const AndroidDownload = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="flex justify-center">
      <a
        href="https://play.google.com/store/apps/details?id=com.atakmap.app.civ&pli=1"
        target="_blank"
        rel="noopener noreferrer"
        className="group inline-flex flex-col items-center gap-2 focus:outline-none"
      >
        <img
          src="/ui/tak/download-buttons/android/googleplay.png"
          width={200}
          alt={t("tabs.android.phase1.step1_desc_civ")}
          className="rounded-md cursor-pointer transition-all
                    group-hover:scale-105
                    group-hover:shadow-lg
                    focus-visible:ring-2
                    focus-visible:ring-primary-light"
        />

        <span className="text-sm font-medium text-primary-light group-hover:underline">
          {t("onboarding.android.downloadFromPlayStore") ||
            "Download from Google Play"}
        </span>
      </a>
    </div>
  );
};
