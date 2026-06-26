import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const WindowsPhase4 = () => {
  const { t } = useTranslation("tak");

  return (
    <div className="space-y-4">
      <Accordion
        type="single"
        collapsible
        defaultValue="step1"
        className="space-y-2"
      >
        {/* Step 1: Check Unit Settings */}
        <AccordionItem value="step1">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase4.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase4.step1_desc_1")}</p>
                <img
                  src="/ui/tak/wintak/Kuva28.png"
                  className="mx-auto pr-12 w-[200px] "
                  alt="Hamburger Menu"
                />
                <p>{t("tabs.windows.phase4.step1_desc_2")}</p>
                <img
                  src="/ui/tak/wintak/Kuva29.png"
                  className="mx-auto pr-5 w-[300px] "
                  alt="Select Settings"
                />
                <p>{t("tabs.windows.phase4.step1_desc_3")}</p>
                <img
                  src="/ui/tak/wintak/Kuva29.png"
                  className="mx-auto pr-5 w-[300px] "
                  alt="Select Display Preferences"
                />
                <p>{t("tabs.windows.phase4.step1_desc_4")}</p>
                <img
                  src="/ui/tak/wintak/Kuva30.png"
                  className="mx-auto pr-5 w-[300px] "
                  alt="Unit Display Preferences"
                />
                <p>{t("tabs.windows.phase4.step1_desc_5")}</p>
                <img
                  src="/ui/tak/wintak/Kuva31.png"
                  className="mx-auto pr-5 w-[300px] "
                  alt="Check Settings"
                />
                <p>{t("tabs.windows.phase4.step1_desc_6")}</p>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2: Troubleshooting */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.windows.phase4.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <p>{t("tabs.windows.phase4.step2_desc")}</p>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
