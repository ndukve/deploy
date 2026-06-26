import { useTranslation } from "react-i18next";

import { InstructionPhase, InstructionsWizard } from "../InstructionWizard";

export const IosInstructionPage = () => {
  const { t } = useTranslation("tak");

  const IOS_PHASES: InstructionPhase[] = [
    { id: 1, title: t("tabs.ios.wizard_title.phase1") },
    { id: 2, title: t("tabs.ios.wizard_title.phase2") },
    { id: 3, title: t("tabs.ios.wizard_title.phase3") },
    { id: 4, title: t("tabs.ios.wizard_title.phase4") },
    { id: 5, title: t("tabs.ios.wizard_title.phase5") },
  ];

  return <InstructionsWizard phases={IOS_PHASES} basePath="/ios" />;
};
