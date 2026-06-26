import { useTranslation } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const IosPhase5 = () => {
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
              {t("tabs.ios.phase5.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.ios.phase5.step1_desc_1")}
                  </p>
                  <img
                    src="/ui/tak/itak/itakquickstart26.png"
                    className="mx-auto w-[400px] p-4 cursor-pointer"
                    alt={t("tabs.ios.phase5.step1_title")}
                  />
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2 */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.ios.phase5.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.ios.phase5.step2_desc_1")}
                  </p>
                  <img
                    src="/ui/tak/itak/itakquickstart27-1.jpeg"
                    className="mx-auto w-[400px] p-4 cursor-pointer"
                    alt={t("tabs.ios.phase5.step2_title")}
                  />
                  <p className="font-medium">
                    {t("tabs.ios.phase5.step2_desc_2")}
                  </p>
                  <img
                    src="/ui/tak/itak/itakquickstart28.png"
                    className="mx-auto w-[400px] p-4 cursor-pointer"
                    alt={t("tabs.ios.phase5.step2_title")}
                  />
                  <p>{t("tabs.ios.phase5.step2_desc_3")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3 */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.ios.phase5.step3_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    {t("tabs.ios.phase5.step3_desc_1")}
                  </p>
                  <img
                    src="/ui/tak/itak/itakquickstart27.png"
                    className="mx-auto w-[400px] p-4 cursor-pointer"
                    alt={t("tabs.ios.phase5.step3_title")}
                  />
                  <p>{t("tabs.ios.phase5.step3_desc_2")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
