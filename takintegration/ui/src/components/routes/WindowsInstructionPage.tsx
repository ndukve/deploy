import { useTranslation } from "react-i18next";

import { InstructionPhase, InstructionsWizard } from "../InstructionWizard";

export const WindowsInstructionPage = () => {
  const { t } = useTranslation("tak");

  const WINDOWS_PHASES: InstructionPhase[] = [
    { id: 1, title: t("tabs.windows.wizard_title.phase1") },
    { id: 2, title: t("tabs.windows.wizard_title.phase2") },
    { id: 3, title: t("tabs.windows.wizard_title.phase3") },
    { id: 4, title: t("tabs.windows.wizard_title.phase4") },
  ];

  return <InstructionsWizard phases={WINDOWS_PHASES} basePath="/windows" />;
};
