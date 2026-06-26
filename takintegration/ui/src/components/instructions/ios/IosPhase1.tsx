import { useTranslation, Trans } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const IosPhase1 = () => {
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
              {t("tabs.ios.phase1.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <h3 className="text-white text-xl">
                    {t("tabs.ios.phase1.step1_desc_title")}
                  </h3>
                  <p className="font-medium">
                    {t("tabs.ios.phase1.step1_desc_1")}
                  </p>
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.ios.phase1.step1_desc_2"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <a href="https://apps.apple.com/us/app/itak/id1561656396">
                    <img
                      src="/ui/tak/download-buttons/ios/app-store-badge.svg"
                      width="200px"
                      alt="App Store"
                      className="mx-auto cursor-pointer"
                    />
                  </a>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
