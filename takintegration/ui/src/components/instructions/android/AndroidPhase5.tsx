import { useTranslation, Trans } from "react-i18next";

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { Card, CardContent } from "@/components/ui/card";

export const AndroidPhase5 = () => {
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
              {t("tabs.android.phase5.step1_title")}
            </AccordionTrigger>
            <AccordionContent className="overflow-x-auto">
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-2 max-w-full break-words">
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase5.step1_desc_1"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/07-Kartta1.png"
                    className="w-full max-w-[500px]"
                    alt={t("tabs.android.phase5.step1_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase5.step1_desc_2"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <img
                    src="/ui/tak/atak/08-OK1.png"
                    className="w-full max-w-[500px]"
                    alt={t("tabs.android.phase5.step1_title")}
                  />
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase5.step1_desc_3"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                  <p className="font-medium">
                    <Trans
                      t={t}
                      i18nKey="tabs.android.phase5.step1_desc_4"
                      components={{ bold: <span className="font-semibold" /> }}
                    />
                  </p>
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 2 */}
        <AccordionItem value="step2">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase5.step2_title")}
            </AccordionTrigger>
            <AccordionContent className="overflow-x-auto">
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-4">
                  <img
                    src="/ui/tak/atak/26-10001.png"
                    className="w-full max-w-[500px]"
                    alt={t("tabs.android.phase5.step2_title")}
                  />
                  <p className="font-medium">
                    {t("tabs.android.phase5.step2_desc_1")}
                  </p>

                  {/* Fixed numbered list */}
                  <ol className="list-decimal space-y-2 pl-8 marker:font-medium">
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_1"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_2"
                        components={{ italic: <em /> }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_3"
                        components={{ italic: <em /> }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_4"
                        components={{ italic: <em /> }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_5"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_6"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step2_desc_2_7"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                  </ol>

                  <p className="font-medium">
                    {t("tabs.android.phase5.step2_desc_3")}
                  </p>
                  <img
                    src="/ui/tak/atak/25-MetersToKilo1.png"
                    className="w-full max-w-[500px]"
                    alt={t("tabs.android.phase5.step2_title")}
                  />
                </div>
              </CardContent>
            </AccordionContent>
          </Card>
        </AccordionItem>

        {/* Step 3 */}
        <AccordionItem value="step3">
          <Card className="p-2">
            <AccordionTrigger className="px-3 py-2 text-left text-base font-semibold">
              {t("tabs.android.phase5.step3_title")}
            </AccordionTrigger>
            <AccordionContent className="overflow-x-auto">
              <CardContent className="p-2 space-y-4 text-sm">
                <div className="pl-4 space-y-4">
                  <p className="font-medium">
                    {t("tabs.android.phase5.step3_desc_1")}
                  </p>

                  {/* Fixed numbered list */}
                  <ol className="list-decimal space-y-2 pl-8 marker:font-medium">
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step3_desc_2_1"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step3_desc_2_2"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step3_desc_2_3"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step3_desc_2_4"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                    <li className="pl-2">
                      <Trans
                        t={t}
                        i18nKey="tabs.android.phase5.step3_desc_2_5"
                        components={{
                          bold: <span className="font-semibold" />,
                        }}
                      />
                    </li>
                  </ol>

                  <img
                    src="/ui/tak/atak/11-Callsign1.png"
                    className="w-full max-w-[500px]"
                    alt={t("tabs.android.phase5.step3_title")}
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
