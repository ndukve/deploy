import { useState } from "react";
import {
  ExternalLink,
  FileText,
  KanbanSquare,
  Presentation,
  Users,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { OnboardingGuide } from "@/components/OnboardingGuide";
import { FeatureGuide } from "@/components/FeatureGuide";
import { Toaster } from "@/components/ui/sonner";
import { useTranslation } from "react-i18next";
import { PRODUCT_SHORTNAME } from "@/App";
import { useMeta } from "@/lib/metadata";
import { buildLoginUrl, type CryptPadCardData } from "@/lib/metadata";

interface FeatureStepDef {
  id: string;
  title: string;
  description: string;
  image: string;
  mobileImage?: string;
}

function getFeatureSteps(featureKey: string): FeatureStepDef[] {
  // Map feature keys to their actual asset folder names
  const folderName = featureKey === "presentations" ? "present" : featureKey;
  const basePath = `/ui/cryptpad/assets/features/${folderName}`;
  const steps: Record<string, FeatureStepDef[]> = {
    docs: [
      {
        id: "docs_intro",
        title: "features.docs.steps.intro.title",
        description: "features.docs.steps.intro.description",
        image: `/ui/cryptpad/assets/cryptpad1.png`,
      },
      {
        id: "docs_create",
        title: "features.docs.steps.create.title",
        description: "features.docs.steps.create.description",
        image: `${basePath}/docs1.png`,
      },
      {
        id: "docs_collaborate",
        title: "features.docs.steps.collaborate.title",
        description: "features.docs.steps.collaborate.description",
        image: `${basePath}/docs2.png`,
      },
      {
        id: "docs_share",
        title: "features.docs.steps.share.title",
        description: "features.docs.steps.share.description",
        image: `${basePath}/docs3.png`,
      },
      {
        id: "docs_onword",
        title: "features.docs.steps.onword.title",
        description: "features.docs.steps.onword.description",
        image: `/ui/cryptpad/assets/cryptpad2.png`,
      },
    ],
    kanban: [
      {
        id: "kanban_intro",
        title: "features.kanban.steps.intro.title",
        description: "features.kanban.steps.intro.description",
        image: `/ui/cryptpad/assets/cryptpad1.png`,
      },
      {
        id: "kanban_create1",
        title: "features.kanban.steps.create1.title",
        description: "features.kanban.steps.create1.description",
        image: `${basePath}/kanban1.png`,
      },
      {
        id: "kanban_create2",
        title: "features.kanban.steps.create2.title",
        description: "features.kanban.steps.create2.description",
        image: `${basePath}/kanban2.png`,
      },
      {
        id: "kanban_manage",
        title: "features.kanban.steps.manage.title",
        description: "features.kanban.steps.manage.description",
        image: `${basePath}/kanban3.png`,
      },
      {
        id: "kanban_situation",
        title: "features.kanban.steps.situation.title",
        description: "features.kanban.steps.situation.description",
        image: `${basePath}/kanban4.png`,
      },
    ],
    presentations: [
      {
        id: "pres_intro",
        title: "features.presentations.steps.intro.title",
        description: "features.presentations.steps.intro.description",
        image: `/ui/cryptpad/assets/cryptpad1.png`,
      },
      {
        id: "pres_create",
        title: "features.presentations.steps.create.title",
        description: "features.presentations.steps.create.description",
        image: `${basePath}/present1.png`,
      },
      {
        id: "pres_present",
        title: "features.presentations.steps.present.title",
        description: "features.presentations.steps.present.description",
        image: `${basePath}/present2.png`,
      },
      {
        id: "pres_onword",
        title: "features.presentations.steps.onword.title",
        description: "features.presentations.steps.onword.description",
        image: `/ui/cryptpad/assets/cryptpad2.png`,
      },
    ],
    unitUse: [
      {
        id: "unit_intro",
        title: "features.unitUse.steps.intro.title",
        description: "features.unitUse.steps.intro.description",
        image: `/ui/cryptpad/assets/cryptpad1.png`,
      },
      {
        id: "unit_setup",
        title: "features.unitUse.steps.setup.title",
        description: "features.unitUse.steps.setup.description",
        image: `/ui/cryptpad/assets/cryptpad2.png`,
      },
      {
        id: "unit_setup1",
        title: "features.unitUse.steps.setup1.title",
        description: "features.unitUse.steps.setup1.description",
        image: `${basePath}/setup1.png`,
      },
      {
        id: "unit_setup2",
        title: "features.unitUse.steps.setup2.title",
        description: "features.unitUse.steps.setup2.description",
        image: `${basePath}/setup2.png`,
      },
      {
        id: "unit_setup3",
        title: "features.unitUse.steps.setup3.title",
        description: "features.unitUse.steps.setup3.description",
        image: `${basePath}/setup3.png`,
      },
      {
        id: "unit_setup4",
        title: "features.unitUse.steps.setup4.title",
        description: "features.unitUse.steps.setup4.description",
        image: `${basePath}/setup4.png`,
      },
      {
        id: "unit_setup5",
        title: "features.unitUse.steps.setup5.title",
        description: "features.unitUse.steps.setup5.description",
        image: `${basePath}/setup5.png`,
      },
      {
        id: "unit_setup6",
        title: "features.unitUse.steps.setup6.title",
        description: "features.unitUse.steps.setup6.description",
        image: `${basePath}/setup6.png`,
      },
      {
        id: "unit_setup7",
        title: "features.unitUse.steps.setup7.title",
        description: "features.unitUse.steps.setup7.description",
        image: `${basePath}/setup7.png`,
      },
      {
        id: "unit_setup8",
        title: "features.unitUse.steps.setup8.title",
        description: "features.unitUse.steps.setup8.description",
        image: `${basePath}/setup8.png`,
      },
      {
        id: "unit_calender1",
        title: "features.unitUse.steps.calender1.title",
        description: "features.unitUse.steps.calender1.description",
        image: `${basePath}/calender1.png`,
      },
      {
        id: "unit_calender2",
        title: "features.unitUse.steps.calender2.title",
        description: "features.unitUse.steps.calender2.description",
        image: `${basePath}/calender2.png`,
      },
      {
        id: "unit_calender3",
        title: "features.unitUse.steps.calender3.title",
        description: "features.unitUse.steps.calender3.description",
        image: `${basePath}/calender3.png`,
      },
      {
        id: "unit_end",
        title: "features.unitUse.steps.end.title",
        description: "features.unitUse.steps.end.description",
        image: `${basePath}/end.png`,
      },
    ],
  };

  return steps[featureKey] || [];
}

interface HomePageProps {
  data: CryptPadCardData;
}

export const HomePage = ({ data }: HomePageProps) => {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const meta = useMeta();
  const loginUrl = buildLoginUrl(data.url);

  const [activeFeature, setActiveFeature] = useState<string | null>(null);

  const featureButtons = [
    {
      key: "docs",
      icon: FileText,
      label: "features.docs.title",
    },
    {
      key: "kanban",
      icon: KanbanSquare,
      label: "features.kanban.title",
    },
    {
      key: "presentations",
      icon: Presentation,
      label: "features.presentations.title",
    },
    {
      key: "unitUse",
      icon: Users,
      label: "features.unitUse.title",
    },
  ];

  return (
    <div className="space-y-8">
      {/* Launch CryptPad Button */}
      <div className="flex justify-center">
        <a
          href={loginUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="w-full"
        >
          <Button
            variant="outline"
            size="lg"
            className="w-full h-auto py-6 cursor-pointer border-2 border-primary/30 hover:border-primary hover:bg-primary/10 hover:shadow-[0_0_18px_2px_hsl(var(--primary)/0.25)] transition-all duration-200 rounded-xl group"
          >
            <div className="flex items-center gap-4 w-full">
              <img
                src="/ui/cryptpad/assets/cryptpad-mark.svg"
                alt=""
                aria-hidden="true"
                className="w-10 h-10 shrink-0 group-hover:scale-110 transition-transform duration-200"
              />
              <div className="flex flex-col items-start text-left min-w-0">
                <span className="text-xl font-bold text-white tracking-tight group-hover:text-primary transition-colors duration-200">
                  {t("home.loginAction")}
                </span>
                <span className="text-sm text-muted-foreground font-normal">
                  {t("home.loginInfo", { callsign: meta.callsign })}
                </span>
              </div>
              <ExternalLink className="w-5 h-5 ml-auto shrink-0 text-muted-foreground group-hover:text-primary transition-colors duration-200" />
            </div>
          </Button>
        </a>
      </div>

      {/* How to use CryptPad's features */}
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-foreground">
          {t("home.featuresTitle")}
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {featureButtons.map(({ key, icon: Icon, label }) => (
            <Button
              key={key}
              variant="outline"
              size="lg"
              className="w-full py-6 cursor-pointer justify-start gap-3"
              onClick={() => setActiveFeature(key)}
            >
              <Icon className="w-5 h-5 text-primary" />
              {t(label)}
            </Button>
          ))}
        </div>
      </div>

      {/* Feature Guide Drawers */}
      {featureButtons.map(({ key }) => (
        <FeatureGuide
          key={key}
          featureKey={key}
          steps={getFeatureSteps(key)}
          open={activeFeature === key}
          onOpenChange={(open) => {
            if (!open) setActiveFeature(null);
          }}
        />
      ))}

      <OnboardingGuide />
      <Toaster position="top-center" />
    </div>
  );
};
