import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const WindowsPhase2 = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="space-y-4">
      <Accordion
        type="single"
        collapsible
        defaultValue="step1"
        className="space-y-2"
      >
        {/* Step 1: Download WinTAK */}
        <AccordionItem value="step1">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase2.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p>{t("tabs.windows.phase2.step1_desc_1")}</p>
                  <a href="https://arkipublic.blob.core.windows.net/ohjelmistot/WinTAK-CIV-latest.zip">
                    <img
                      src="/ui/tak/wintak/windownload.svg"
                      width="200px"
                      alt={t("tabs.windows.phase2.step1_title")}
                    />
                  </a>
                  <p className="text-red-400 mt-2">
                    {t("tabs.windows.phase2.step1_desc_2")}
                  </p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2: Open the Installer */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase2.step3_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p>{t("tabs.windows.phase2.step3_desc_1")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva9.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step3_title")}
                  />
                  <p>{t("tabs.windows.phase2.step3_desc_2")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva10.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step3_desc_2")}
                  />
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3: Install Using the Installer */}
        <AccordionItem value="step4">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase2.step4_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p>{t("tabs.windows.phase2.step4_desc_1")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva11.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step4_desc_1")}
                  />
                  <p>{t("tabs.windows.phase2.step4_desc_2")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva12.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step4_desc_2")}
                  />
                  <p>{t("tabs.windows.phase2.step4_desc_3")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva13.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step4_desc_3")}
                  />
                  <p>{t("tabs.windows.phase2.step4_desc_4")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva13-1.png"
                    width="400px"
                    alt={t("tabs.windows.phase2.step4_desc_4")}
                  />
                  <p>{t("tabs.windows.phase2.step4_desc_5")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
