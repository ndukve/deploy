import { Link } from "@tanstack/react-router";
import { useTranslation } from "react-i18next";

import { Button } from "../ui/button";
import { ZipButton } from "../ZipButton";

import { TAK_Zip } from "@/lib/interfaces";

interface Props {
  zip: TAK_Zip;
}

export function IosTab({ zip }: Props) {
  const { t } = useTranslation("tak");

  return (
    <div className="mt-4">
      <p className="text-lg font-semibold">{t("tabs.ios.title")}</p>
      <div className="font-normal">
        <p>{t("tabs.ios.step1_download")}</p>
        <ZipButton
          data={zip.data}
          text={zip.title}
          filename={zip.filename}
          className="p-2"
        />
      </div>
      <div className="mt-4">
        <p className="mb-2">{t("tabs.ios.instructions_short")}</p>
        <Button asChild variant="secondary">
          {/* eslint-disable-next-line */}
          <Link to={"/ios/1" as any}>{t("tabs.ios.open_instructions")}</Link>
        </Button>
      </div>
    </div>
  );
}
