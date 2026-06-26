import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const AndroidPhase1 = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="space-y-4">
      <Accordion
        type="single"
        collapsible
        defaultValue="step1"
        className="space-y-2"
      >
        {/* Step 1 */}
        <AccordionItem value="step1">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase1.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-6 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.android.phase1.step1_desc_civ")}
                  </p>
                  <a href="https://play.google.com/store/apps/details?id=com.atakmap.app.civ&pli=1">
                    <img
                      src="/ui/tak/download-buttons/android/googleplay.png"
                      width="200"
                      className="rounded-md shadow-sm"
                      alt={t("tabs.android.phase1.step1_desc_civ")}
                    />
                  </a>
                </div>

                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.android.phase1.step1_desc_sync")}
                  </p>
                  <a href="https://play.google.com/store/apps/details?id=com.atakmap.android.datasync.plugin">
                    <img
                      src="/ui/tak/download-buttons/android/googleplay.png"
                      width="200"
                      className="rounded-md shadow-sm"
                      alt={t("tabs.android.phase1.step1_desc_sync")}
                    />
                  </a>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2 */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase1.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-1">
                  <p className="font-medium">
                    {t("tabs.android.phase1.step2_desc_permissions")}
                  </p>
                  <p>{t("tabs.android.phase1.step2_desc_error")}</p>
                  <img
                    src="/ui/tak/atak/wait.png"
                    width="200"
                    className="rounded-md shadow-sm"
                    alt={t("tabs.android.phase1.step2_desc_error")}
                  />
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
