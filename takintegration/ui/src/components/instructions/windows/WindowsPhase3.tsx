import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const WindowsPhase3 = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="space-y-4">
      <Accordion
        type="single"
        collapsible
        defaultValue="step1"
        className="space-y-2"
      >
        {/* Step 1: Open the Application */}
        <AccordionItem value="step1">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step1_desc")}</p>
                <img
                  src="/ui/tak/wintak/Kuva14.png"
                  className="mx-auto pr-5 w-[90px] "
                  alt="Open the Application"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2: Accept the EULA */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step2_desc_1")}</p>
                <p>{t("tabs.windows.phase3.step2_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva16.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Accept EULA"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3: Establish Server Connection */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step3_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step3_desc_1")}</p>
                <p>{t("tabs.windows.phase3.step3_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva17.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Establish Server Connection"
                />
                <p>{t("tabs.windows.phase3.step3_desc_3")}</p>
                <img
                  src="/ui/tak/wintak/Kuva18.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Choose Client Package"
                />
                <p>{t("tabs.windows.phase3.step3_desc_4")}</p>
                <img
                  src="/ui/tak/wintak/Kuva19.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Import Strategy"
                />
                <p>{t("tabs.windows.phase3.step3_desc_5")}</p>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 4: Choose a Map Base */}
        <AccordionItem value="step4">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step4_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step4_desc_1")}</p>
                <img
                  src="/ui/tak/wintak/Kuva20.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Choose a Map Base"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 5: Set Callsign */}
        <AccordionItem value="step5">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step5_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step5_desc_1")}</p>
                <img
                  src="/ui/tak/wintak/Kuva21.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Set Callsign"
                />
                <p>{t("tabs.windows.phase3.step5_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva23.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Additional WMS"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 6: Set Plugins */}
        <AccordionItem value="step6">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step6_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step6_desc_1")}</p>
                <img
                  src="/ui/tak/wintak/Kuva24.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Set Plugins"
                />
                <p>{t("tabs.windows.phase3.step6_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva25.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="DTED-0 Models"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 7: Review Settings */}
        <AccordionItem value="step7">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase3.step7_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase3.step7_desc_1")}</p>
                <img
                  src="/ui/tak/wintak/Kuva26.png"
                  className="mx-auto pr-5 w-[400px] "
                  alt="Review Settings"
                />
                <p>{t("tabs.windows.phase3.step7_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva27.png"
                  className="mx-auto pr-10 w-[200px] "
                  alt="TAK Network Status"
                />
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
