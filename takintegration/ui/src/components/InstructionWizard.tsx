import { useNavigate, useParams } from "@tanstack/react-router";
import { Outlet } from "@tanstack/react-router";
import { ChevronLeft, ChevronRight } from "lucide-react";
import React from "react";
import { useTranslation } from "react-i18next";

import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";

export interface InstructionPhase {
  id: number;
  title: string;
}

interface InstructionsWizardProps {
  phases: InstructionPhase[];
  basePath: string;
  showPhaseNumbers?: boolean;
  onCompleteRedirect?: string;
}

export const InstructionsWizard: React.FC<InstructionsWizardProps> = ({
  phases,
  basePath,
  showPhaseNumbers = true,
  onCompleteRedirect = "/",
}) => {
  const { t } = useTranslation("tak");
  const navigate = useNavigate();
  const params: { phaseId?: string } = useParams({
    // @ts-expect-error dynamic basePath isn't representable in the router's typed param map
    from: `${basePath}/$phaseId`,
  });
  const phaseIdParam = params.phaseId;
  const phaseId = phaseIdParam ? parseInt(phaseIdParam, 10) : phases[0].id;

  const currentPhaseIndex = phases.findIndex((p) => p.id === phaseId);
  const currentPhase = phases[currentPhaseIndex] || phases[0];
  const progressPercentage = ((currentPhaseIndex + 1) / phases.length) * 100;

  const handleNext = () => {
    if (currentPhaseIndex < phases.length - 1) {
      void navigate({
        to: `${basePath}/${phases[currentPhaseIndex + 1].id}`,
      });
    } else {
      void navigate({ to: onCompleteRedirect });
    }
  };

  const handlePrevious = () => {
    if (currentPhaseIndex > 0) {
      void navigate({
        to: `${basePath}/${phases[currentPhaseIndex - 1].id}`,
      });
    }
  };

  const handlePhaseClick = (index: number) => {
    void navigate({ to: `${basePath}/${phases[index].id}` });
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Top bar */}
      <div className="px-6 pt-6 pb-4 space-y-2">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold">
            {showPhaseNumbers && (
              <span className="text-sm text-muted-foreground">
                {t("wizard.step_counter", {
                  current: currentPhaseIndex + 1,
                  total: phases.length,
                })}
              </span>
            )}
          </h2>
        </div>
        <Progress value={progressPercentage} />
      </div>

      <h1 className="text-2xl font-bold px-6">{currentPhase.title}</h1>

      <div className="px-6 py-6">
        <Outlet />
      </div>

      {/* Navigation  */}
      <div className="w-full bg-background border-t p-4 md:p-6 flex items-center justify-between gap-2">
        <Button
          variant="outline"
          onClick={handlePrevious}
          disabled={currentPhaseIndex <= 0}
          className="gap-2 px-4 py-2 md:py-3 shrink-0"
        >
          <ChevronLeft className="w-4 h-4" />
          <span className="hidden md:inline">{t("wizard.previous")}</span>
        </Button>

        {/* Phase dots */}
        <div className="flex flex-1 justify-center gap-2">
          {phases.map((_, index) => (
            <button
              key={index}
              onClick={() => handlePhaseClick(index)}
              className={`rounded-full transition-all ${
                index === currentPhaseIndex
                  ? "bg-primary w-6 h-2 md:w-8 md:h-2"
                  : "bg-secondary w-2 h-2 md:w-2 md:h-2 hover:bg-secondary/70"
              }`}
              aria-label={`Go to phase ${index + 1}`}
            />
          ))}
        </div>

        <Button
          onClick={handleNext}
          className="gap-2 px-4 py-2 md:py-3 shrink-0"
        >
          <span className="hidden md:inline">
            {currentPhaseIndex === phases.length - 1
              ? t("wizard.complete")
              : t("wizard.next")}
          </span>
          <ChevronRight className="w-4 h-4" />
        </Button>
      </div>
    </div>
  );
};
