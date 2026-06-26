import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const WindowsPhase1 = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="space-y-4">
      <Accordion
        type="single"
        collapsible
        defaultValue="step1"
        className="space-y-2"
      >
        {/* Step 1: Set Region to United States */}
        <AccordionItem value="step1">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase1.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.windows.phase1.step1_desc_1")}
                  </p>
                  <img
                    src="/ui/tak/wintak/Kuva1.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step1_title")}
                  />
                  <p>{t("tabs.windows.phase1.step1_desc_2")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva2.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step1_desc_2")}
                  />
                  <p>{t("tabs.windows.phase1.step1_desc_3")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva3.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step1_desc_3")}
                  />
                  <p>{t("tabs.windows.phase1.step1_desc_4")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2: Set Language to English (US) */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase1.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <img
                    src="/ui/tak/wintak/Kuva4.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step2_title")}
                  />
                  <p>{t("tabs.windows.phase1.step2_desc_1")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva5.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step2_desc_2")}
                  />
                  <p>{t("tabs.windows.phase1.step2_desc_2")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva8.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step2_desc_3")}
                  />
                  <p>{t("tabs.windows.phase1.step2_desc_3")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3: If Necessary, Add Language Pack (English) */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase1.step3_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p>{t("tabs.windows.phase1.step3_desc_1")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva6.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step3_desc_1")}
                  />
                  <p>{t("tabs.windows.phase1.step3_desc_2")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva7.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step3_desc_2")}
                  />
                  <p>{t("tabs.windows.phase1.step3_desc_3")}</p>
                  <img
                    src="/ui/tak/wintak/Kuva8.png"
                    width="400px"
                    alt={t("tabs.windows.phase1.step3_desc_3")}
                  />
                  <p>{t("tabs.windows.phase1.step3_desc_4")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
