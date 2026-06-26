import { useTranslation, Trans } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const AndroidPhase4 = () => {
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
              {t("tabs.android.phase4.step1_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step1_desc_1"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync111.jpg"
                    width="500px"
                    alt={t("tabs.android.phase4.step1_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step1_desc_2"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync12.jpg"
                    width="500px"
                    alt={t("tabs.android.phase4.step1_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step1_desc_3"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync13.jpg"
                    width="500px"
                    alt={t("tabs.android.phase4.step1_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step1_desc_4"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync14.jpg"
                    width="500px"
                    alt={t("tabs.android.phase4.step1_title")}
                  />
                  <p>{t("tabs.android.phase4.step1_desc_5")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2 */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase4.step2_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step2_desc_1"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync1.png"
                    width="500px"
                    alt={t("tabs.android.phase4.step2_title")}
                  />
                  <p>{t("tabs.android.phase4.step2_desc_2")}</p>
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step2_desc_3"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/datasyncatak99.png"
                    width="500px"
                    alt={t("tabs.android.phase4.step2_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step2_desc_4"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync3.png"
                    width="500px"
                    alt={t("tabs.android.phase4.step2_title")}
                  />
                  <p>{t("tabs.android.phase4.step2_desc_5")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3 */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase4.step3_title")}
            </AccordionTrigger>
            <AccordionContent>
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2">
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step3_desc_1"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step3_desc_2"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync4.png"
                    width="500px"
                    alt={t("tabs.android.phase4.step3_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase4.step3_desc_3"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/atakdatasync5.png"
                    width="500px"
                    alt={t("tabs.android.phase4.step3_title")}
                  />
                  <p>{t("tabs.android.phase4.step3_desc_4")}</p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>
      </Accordion>
    </div>
  );
};
