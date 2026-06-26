import { ChevronRight, ChevronLeft, Info } from "lucide-react";
import { useState, useEffect, useCallback, useMemo } from "react";
import { useTranslation } from "react-i18next";
import { toast } from "sonner";

import { AndroidDownload } from "./android/AndroidDownload";
import { IosDownload } from "./ios/IosDownload";

import { Button } from "@/components/ui/button";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import useHealthCheck from "@/hooks/helpers/useHealthcheck";
import { useMetadata } from "@/hooks/use-metadata";
import { useIsMobile } from "@/hooks/use-mobile";
import { detectPlatform, Platform } from "@/lib/detectPlatform";
import { cn } from "@/lib/utils";

const hashString = (str: string): string => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash;
  }
  return Math.abs(hash).toString(36).padStart(8, "0").slice(0, 8);
};

interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  image: string;
  mobileImage?: string;
  customComponent?: React.ComponentType;
}

const ONBOARDING_STEPS: Record<Platform, OnboardingStep[]> = {
  [Platform.Android]: [
    {
      id: "atak-welcome",
      title: "onboarding.android.steps.tak-welcome.title",
      description: "onboarding.android.steps.tak-welcome.description",
      image: "/ui/tak/assets/Onboarding/WELCOME.png",
      mobileImage: "/ui/tak/assets/Onboarding/WELCOME.png",
    },
    {
      id: "atak-download",
      title: "onboarding.android.steps.tak-download.title",
      description: "onboarding.android.steps.tak-download.description",
      image: "/ui/tak/assets/Onboarding/android/tak/atak_install.png",
      mobileImage: "/ui/tak/assets/Onboarding/android/tak/atak_install.png",
      customComponent: AndroidDownload,
    },
    {
      id: "atak-return",
      title: "onboarding.general.steps.return.title",
      description: "onboarding.general.steps.return.description",
      image: "/ui/tak/assets/Onboarding/RETURN.png",
      mobileImage: "/ui/tak/assets/Onboarding/RETURN.png",
    },
    {
      id: "atak-auto-import",
      title: "onboarding.android.steps.tak-auto-import.title",
      description: "onboarding.android.steps.tak-auto-import.description",
      image: "/ui/tak/assets/Onboarding/AUTO_IMPORT.png",
      mobileImage:
        "/ui/tak/assets/Onboarding/android/default/auto_connect.webp",
    },
    {
      id: "atak-home",
      title: "onboarding.android.steps.tak-home.title",
      description: "onboarding.android.steps.tak-home.description",
      image: "/ui/tak/assets/Onboarding/android/tak/atak_home(1).png",
      mobileImage: "/ui/tak/assets/Onboarding/android/tak/atak_home(1).png",
    },
    {
      id: "atak-plugins",
      title: "onboarding.android.steps.tak-plugins.title",
      description: "onboarding.android.steps.tak-plugins.description",
      image: "/ui/tak/assets/Onboarding/android/tak/atak_plugins(1).png",
      mobileImage: "/ui/tak/assets/Onboarding/android/tak/atak_plugins(1).png",
    },
    {
      id: "atak-data-sync",
      title: "onboarding.android.steps.tak-data-sync.title",
      description: "onboarding.android.steps.tak-data-sync.description",
      image: "/ui/tak/assets/Onboarding/android/tak/atak_plugin_load.png",
      mobileImage: "/ui/tak/assets/Onboarding/android/tak/atak_plugin_load.png",
    },
  ],
  [Platform.iOS]: [
    {
      id: "ios-welcome",
      title: "onboarding.ios.steps.welcome.title",
      description: "onboarding.ios.steps.welcome.description",
      image: "/ui/tak/assets/Onboarding/WELCOME.png",
      mobileImage: "/ui/tak/assets/Onboarding/WELCOME.png",
    },
    {
      id: "ios-download",
      title: "onboarding.ios.steps.tak-download.title",
      description: "onboarding.ios.steps.tak-download.description",
      image: "/ui/tak/assets/Onboarding/ios/download.png",
      mobileImage: "/ui/tak/assets/Onboarding/ios/download.png",
      customComponent: IosDownload,
    },
    {
      id: "ios-return",
      title: "onboarding.general.steps.return.title",
      description: "onboarding.general.steps.return.description",
      image: "/ui/tak/assets/Onboarding/RETURN.png",
      mobileImage: "/ui/tak/assets/Onboarding/RETURN.png",
    },
    {
      id: "ios-package",
      title: "onboarding.ios.steps.tak-package.title",
      description: "onboarding.ios.steps.tak-package.description",
      image: "/ui/tak/assets/Onboarding/ios/package_download.png",
      mobileImage: "/ui/tak/assets/Onboarding/ios/package_download.png",
    },
    {
      id: "ios-setup",
      title: "onboarding.ios.steps.itak-setup.title",
      description: "onboarding.ios.steps.itak-setup.description",
      image: "/ui/tak/assets/Onboarding/ios/itak_pages.webp",
      mobileImage: "/ui/tak/assets/Onboarding/ios/itak_pages.webp",
    },
    {
      id: "ios-settings",
      title: "onboarding.ios.steps.itak-settings.title",
      description: "onboarding.ios.steps.itak-settings.description",
      image: "/ui/tak/assets/Onboarding/ios/itak_settings.webp",
      mobileImage: "/ui/tak/assets/Onboarding/ios/itak_settings.webp",
    },
    {
      id: "ios-import",
      title: "onboarding.ios.steps.itak-import.title",
      description: "onboarding.ios.steps.itak-import.description",
      image: "/ui/tak/assets/Onboarding/ios/itak_package.webp",
      mobileImage: "/ui/tak/assets/Onboarding/ios/itak_package.webp",
    },

    {
      id: "ios-sync1",
      title: "onboarding.ios.steps.itak-sync1.title",
      description: "onboarding.ios.steps.itak-sync1.description",
      image: "/ui/tak/assets/Onboarding/ios/itak_sync1.webp",
      mobileImage: "/ui/tak/assets/Onboarding/ios/itak_sync1.webp",
    },
    {
      id: "ios-sync2",
      title: "onboarding.ios.steps.itak-sync2.title",
      description: "onboarding.ios.steps.itak-sync2.description",
      image: "/ui/tak/assets/Onboarding/ios/itak_sync2.webp",
      mobileImage: "/ui/tak/assets/Onboarding/ios/itak_sync2.webp",
    },
  ],
  [Platform.Windows]: [
    {
      id: "tak-welcome",
      title: "onboarding.general.steps.welcome.title",
      description: "onboarding.general.steps.welcome.description",
      image: "/ui/tak/assets/Onboarding/WELCOME.png",
      mobileImage: "/ui/tak/assets/Onboarding/WELCOME.png",
    },
    {
      id: "windows-import",
      title: "onboarding.general.steps.install.title",
      description: "onboarding.wintak.description",
      image: "/ui/tak/assets/Onboarding/general/wintak.png",
      mobileImage: "/ui/tak/assets/Onboarding/general/wintak.png",
    },
  ],
  [Platform.Tracker]: [
    {
      id: "tracker-welcome",
      title: "onboarding.general.steps.welcome.title",
      description: "onboarding.general.steps.welcome.description",
      image: "/ui/tak/assets/Onboarding/WELCOME.png",
      mobileImage: "/ui/tak/assets/Onboarding/WELCOME.png",
    },
    {
      id: "tracker-import",
      title: "onboarding.general.steps.install.title",
      description: "onboarding.general.steps.install.description",
      image: "/ui/tak/assets/Onboarding/general/download.png",
      mobileImage: "/ui/tak/assets/Onboarding/general/download.png",
    },
  ],
};

export function OnboardingHandler() {
  const { t } = useTranslation("tak");
  const { deployment } = useHealthCheck();
  const isMobile = useIsMobile();
  const metadata = useMetadata();

  const defaultPlatform = detectPlatform();
  const [platform, setPlatform] = useState<Platform>(defaultPlatform);

  const [open, setOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState<string[]>([]);
  const [initialized, setInitialized] = useState(false);

  const [imageEnlarged, setImageEnlarged] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  const relevantSteps = useMemo(
    () => ONBOARDING_STEPS[platform] || [],
    [platform],
  );

  const storageKeys = useMemo(() => {
    console.log("Storage key change");
    if (!metadata.callsign || !deployment) return null;
    const deploymentHash = hashString(deployment);
    const base = `${deploymentHash}-tak-onboarding-${metadata.callsign}-${platform}`;
    return {
      finished: `${base}-finished`,
      steps: `${base}-steps`,
      session: `${base}-session`,
      platform: `${deploymentHash}-tak-onboarding-${metadata.callsign}-platform`,
    };
  }, [deployment, metadata.callsign, platform]);

  useEffect(() => {
    if (!storageKeys || initialized) return;

    const finished = localStorage.getItem(storageKeys.finished) === "true";
    const stepsRaw = localStorage.getItem(storageKeys.steps);
    const sessionRaw = localStorage.getItem(storageKeys.session);

    let savedSteps: string[] = [];
    if (stepsRaw) {
      try {
        savedSteps = JSON.parse(stepsRaw) as string[];
        setCompleted(savedSteps);
      } catch (e) {
        console.error(e);
      }
    }

    const firstIncomplete = relevantSteps.findIndex(
      (s) => !savedSteps.includes(s.id),
    );
    const targetStep =
      firstIncomplete !== -1
        ? firstIncomplete
        : Math.max(0, relevantSteps.length - 1);

    if (sessionRaw) {
      try {
        const { stepIndex } = JSON.parse(sessionRaw) as { stepIndex: number };
        const shouldRestoreStep =
          stepIndex >= 0 &&
          stepIndex < relevantSteps.length &&
          !savedSteps.includes(relevantSteps[stepIndex].id);
        setCurrentStep(shouldRestoreStep ? stepIndex : targetStep);
      } catch (e) {
        console.error(e);
        setCurrentStep(targetStep);
      }
    } else {
      setCurrentStep(targetStep);
    }

    if (!finished && firstIncomplete !== -1) {
      setOpen(true);
    }

    setInitialized(true);
  }, [storageKeys, initialized, relevantSteps]);

  useEffect(() => {
    if (storageKeys && initialized) {
      localStorage.setItem(
        storageKeys.session,
        JSON.stringify({
          stepIndex: currentStep,
        }),
      );
    }
  }, [currentStep, storageKeys, initialized]);

  useEffect(() => {
    if (!initialized || !storageKeys) return;

    setImageLoading(true);
    setImageError(false);

    const stepsRaw = localStorage.getItem(storageKeys.steps);
    if (stepsRaw) {
      try {
        const savedSteps = JSON.parse(stepsRaw) as string[];
        setCompleted(savedSteps);

        const firstIncomplete = relevantSteps.findIndex(
          (s) => !savedSteps.includes(s.id),
        );
        if (firstIncomplete !== -1) {
          setCurrentStep(firstIncomplete);
        } else {
          setCurrentStep(0);
        }
      } catch (e) {
        console.error(e);
        setCurrentStep(0);
        setCompleted([]);
      }
    } else {
      setCurrentStep(0);
      setCompleted([]);
    }
  }, [platform, initialized, storageKeys, relevantSteps]);

  const handleOpenChange = useCallback((newOpen: boolean) => {
    setOpen(newOpen);
  }, []);

  const handleNext = () => {
    if (currentStep < relevantSteps.length - 1) {
      setImageLoading(true);
      setImageError(false);
      setImageEnlarged(false);
      setCurrentStep((prev) => prev + 1);
    }
  };

  const handleComplete = () => {
    const step = relevantSteps[currentStep];
    const nextCompleted = Array.from(new Set([...completed, step.id]));
    setCompleted(nextCompleted);

    if (storageKeys) {
      localStorage.setItem(storageKeys.steps, JSON.stringify(nextCompleted));
      if (currentStep === relevantSteps.length - 1) {
        localStorage.setItem(storageKeys.finished, "true");
        setOpen(false);
        toast.success(t("onboarding.completion"));
      } else {
        handleNext();
      }
    }
  };

  if (!initialized || !storageKeys || isMobile === undefined) return null;

  const step = relevantSteps[currentStep];
  if (!step) return null;

  const progress = ((currentStep + 1) / relevantSteps.length) * 100;
  const imageUrl = isMobile && step.mobileImage ? step.mobileImage : step.image;

  const contentComponent = (
    <div className="flex flex-col h-full max-h-[85vh] w-full overflow-hidden">
      <div className="flex-1 overflow-y-auto min-h-0 p-4 md:p-6 space-y-6">
        <div className="space-y-1">
          <h2 className="text-xl font-bold leading-tight">{t(step.title)}</h2>
          <p className="text-xs text-muted-foreground uppercase tracking-wider font-semibold">
            {t("onboarding.step")} {currentStep + 1} / {relevantSteps.length}
          </p>
          <div className="mt-4">
            <Select
              value={platform}
              onValueChange={(value) => setPlatform(value as Platform)}
            >
              <SelectTrigger className="w-full">
                <SelectValue placeholder={t("platform.select_placeholder")} />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value={Platform.Android}>
                  <img
                    src="/ui/tak/android.svg"
                    className="h-4 inline mr-2"
                    alt=""
                  />{" "}
                  {t("platform.android")}
                </SelectItem>
                <SelectItem value={Platform.iOS}>
                  <img
                    src="/ui/tak/apple.svg"
                    className="h-4 inline mr-2"
                    alt=""
                  />{" "}
                  {t("platform.ios")}
                </SelectItem>
                <SelectItem value={Platform.Windows}>
                  <img
                    src="/ui/tak/windows.svg"
                    className="h-4 inline mr-2"
                    alt=""
                  />{" "}
                  {t("platform.windows")}
                </SelectItem>
                <SelectItem value={Platform.Tracker}>
                  <img
                    src="/ui/tak/android.svg"
                    className="h-4 inline mr-1"
                    alt=""
                  />{" "}
                  /{" "}
                  <img
                    src="/ui/tak/apple.svg"
                    className="h-4 inline ml-1"
                    alt=""
                  />{" "}
                  {t("platform.tracker")}
                </SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div
          className={cn(
            "relative rounded-xl overflow-hidden aspect-video w-full border border-border shadow-sm bg-muted/20 shrink-0",
            !imageError && !imageLoading && "cursor-pointer",
          )}
          onClick={() => !imageError && !imageLoading && setImageEnlarged(true)}
        >
          {imageLoading && !imageError && (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="w-8 h-8 border-2 border-primary-light border-t-transparent rounded-full animate-spin" />
            </div>
          )}
          <img
            src={imageUrl}
            key={`${platform}`}
            alt="Onboarding"
            className={cn(
              "w-full h-full object-contain transition-opacity duration-300",
              imageLoading ? "opacity-0" : "opacity-100",
            )}
            onLoad={() => setImageLoading(false)}
            onError={() => {
              setImageError(true);
              setImageLoading(false);
            }}
          />
        </div>

        <div className="text-sm text-muted-foreground leading-relaxed">
          {t(step.description)}
          {step.customComponent && (
            <div className="mt-4">
              <step.customComponent />
            </div>
          )}
        </div>
      </div>

      <div className="p-4 border-t bg-background flex gap-3 shrink-0 mt-auto">
        <Button
          variant="outline"
          onClick={() => currentStep > 0 && setCurrentStep((c) => c - 1)}
          disabled={currentStep === 0}
          className="flex-1"
        >
          <ChevronLeft className="w-4 h-4 mr-2" /> {t("onboarding.back")}
        </Button>
        <Button
          onClick={handleComplete}
          className="flex-1 bg-primary-light hover:bg-primary-light/90 text-white"
        >
          {currentStep === relevantSteps.length - 1
            ? t("onboarding.finish")
            : t("onboarding.next")}
          <ChevronRight className="w-4 h-4 ml-2" />
        </Button>
      </div>

      <div className="h-1.5 w-full bg-muted shrink-0">
        <div
          className="h-full bg-primary-light transition-all duration-500 ease-out"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );

  return (
    <>
      {!open && (
        <button
          onClick={() => {
            const firstIncomplete = relevantSteps.findIndex(
              (s) => !completed.includes(s.id),
            );
            if (firstIncomplete !== -1) {
              setCurrentStep(firstIncomplete);
            } else {
              setCurrentStep(0);
            }
            setOpen(true);
          }}
          className="fixed bottom-6 right-6 p-3 rounded-full bg-primary-light text-white shadow-xl z-50 hover:scale-110 transition-transform active:scale-95"
        >
          <Info className="w-6 h-6" />
        </button>
      )}

      <Dialog open={imageEnlarged} onOpenChange={setImageEnlarged}>
        <DialogContent className="max-w-[95vw] h-[90vh] p-0 bg-black/95 border-none flex items-center justify-center">
          <DialogTitle className="sr-only"></DialogTitle>
          <img
            src={imageUrl}
            alt="Preview"
            className="max-w-full max-h-full object-contain"
          />
        </DialogContent>
      </Dialog>

      {isMobile ? (
        <Drawer open={open} onOpenChange={handleOpenChange}>
          <DrawerContent>{contentComponent}</DrawerContent>
        </Drawer>
      ) : (
        <Dialog open={open} onOpenChange={handleOpenChange}>
          <DialogContent className="max-w-2xl max-h-[90vh] p-0 flex flex-col overflow-hidden outline-none">
            {contentComponent}
          </DialogContent>
        </Dialog>
      )}
    </>
  );
}
