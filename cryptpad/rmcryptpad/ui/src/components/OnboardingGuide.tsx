import { useState, useEffect, useCallback, useRef, useMemo } from "react";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { PRODUCT_SHORTNAME } from "@/App";
import { Button } from "@/components/ui/button";
import { ChevronRight, ChevronLeft, ImageOff, Info } from "lucide-react";
import { useIsMobile } from "@/hooks/use-mobile";
import { toast } from "sonner";
import { useTranslation } from "react-i18next";
import useHealthCheck from "@/hooks/helpers/useHealthcheck";
import { cn } from "@/lib/utils";
import { useMeta } from "@/lib/metadata";

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
}

function ONBOARDING_STEPS(): OnboardingStep[] {
  return [
    {
      id: "welcome",
      title: "onboarding.steps.welcome.title",
      description: "onboarding.steps.welcome.description",
      image: `/ui/cryptpad/assets/cryptpad1.png`,
    },
    {
      id: "what_is_cryptpad",
      title: "onboarding.steps.whatIs.title",
      description: "onboarding.steps.whatIs.description",
      image: `/ui/cryptpad/assets/e2e.png`,
    },
    {
      id: "sign_in",
      title: "onboarding.steps.signIn.title",
      description: "onboarding.steps.signIn.description",
      image: `/ui/cryptpad/assets/cryptpad4.png`,
    },
    {
      id: "dashboard",
      title: "onboarding.steps.dashboard.title",
      description: "onboarding.steps.dashboard.description",
      image: `/ui/cryptpad/assets/cryptpad2.png`,
    },
    {
      id: "create_document",
      title: "onboarding.steps.createDoc.title",
      description: "onboarding.steps.createDoc.description",
      image: `/ui/cryptpad/assets/cryptpad3.png`,
    },
    {
      id: "share",
      title: "onboarding.steps.share.title",
      description: "onboarding.steps.share.description",
      image: `/ui/cryptpad/assets/share.png`,
    },
  ];
}

const getOnboardingImage = (
  step: OnboardingStep,
  isMobile: boolean,
  forceDesktop = false,
): string => {
  const imagePath = forceDesktop
    ? step.image
    : isMobile && step.mobileImage
    ? step.mobileImage
    : step.image;

  return imagePath;
};

const imageCache = new Map<string, { loaded: boolean; error: boolean }>();

const preloadImage = (src: string): Promise<void> => {
  if (imageCache.has(src)) {
    return Promise.resolve();
  }

  return new Promise((resolve) => {
    const img = new Image();
    img.onload = () => {
      imageCache.set(src, { loaded: true, error: false });
      resolve();
    };
    img.onerror = () => {
      imageCache.set(src, { loaded: true, error: true });
      resolve();
    };
    img.src = src;
  });
};

export function OnboardingGuide() {
  const [open, setOpen] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [completed, setCompleted] = useState<string[]>([]);
  const [showCompletion, setShowCompletion] = useState(false);
  const [, setCanReview] = useState(false);
  const [reviewMode, setReviewMode] = useState(false);
  const [imageEnlarged, setImageEnlarged] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const preloadedForDeviceRef = useRef<boolean | null>(null);
  const isMobile = useIsMobile();
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const { deployment } = useHealthCheck();
  const meta = useMeta();

  const relevantSteps = useMemo(() => ONBOARDING_STEPS(), []);

  useEffect(() => {
    if (isMobile === undefined || relevantSteps.length === 0) return;
    if (preloadedForDeviceRef.current === isMobile) return;

    preloadedForDeviceRef.current = isMobile;

    const preloadAllImages = async () => {
      const inlineImages = relevantSteps.map((step) =>
        getOnboardingImage(step, isMobile, false),
      );
      const desktopImages = relevantSteps.map((step) =>
        getOnboardingImage(step, isMobile, true),
      );
      await Promise.all([...inlineImages, ...desktopImages].map(preloadImage));
    };

    void preloadAllImages();
  }, [relevantSteps, isMobile]);

  const checkImageCache = useCallback((url: string) => {
    const cached = imageCache.get(url);
    if (cached) {
      setImageLoading(false);
      setImageError(cached.error);
    } else {
      setImageLoading(true);
      setImageError(false);
    }
  }, []);

  useEffect(() => {
    if (!meta.callsign || !deployment) return;

    const deploymentHash = hashString(deployment);
    const storageKey = `${deploymentHash}-cryptpad-onboarding-${meta.callsign}`;
    const seenOnboarding = localStorage.getItem(storageKey);

    const completedSteps = localStorage.getItem(
      `${deploymentHash}-cryptpad-onboarding-steps-${meta.callsign}`,
    );

    if (!seenOnboarding) {
      setOpen(true);
    }

    if (completedSteps) {
      const parsedCompleted = JSON.parse(completedSteps) as string[];
      setCompleted(parsedCompleted);

      if (parsedCompleted.length > 0 && !seenOnboarding) {
        const firstIncompleteIndex = relevantSteps.findIndex(
          (step) => !parsedCompleted.includes(step.id),
        );
        if (firstIncompleteIndex !== -1) {
          setCurrentStep(firstIncompleteIndex);
        } else {
          setCurrentStep(relevantSteps.length - 1);
        }
        setCanReview(true);
      }
    }
  }, [meta.callsign, deployment, relevantSteps]);

  useEffect(() => {
    if (
      relevantSteps.length > 0 &&
      isMobile !== undefined &&
      relevantSteps[currentStep]
    ) {
      const url = getOnboardingImage(
        relevantSteps[currentStep],
        isMobile,
        false,
      );
      if (url) {
        checkImageCache(url);
      }
    }
  }, [currentStep, relevantSteps, checkImageCache, isMobile]);

  const handleNext = () => {
    if (currentStep < relevantSteps.length - 1) {
      setCurrentStep(currentStep + 1);
      setImageError(false);
      setImageLoading(true);
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
      setImageError(false);
      setImageLoading(true);
    }
  };

  const handleReviewClick = () => {
    setReviewMode(true);
    setCurrentStep(0);
    setOpen(true);
  };

  const handleOpenChange = (newOpen: boolean) => {
    setOpen(newOpen);
    if (!newOpen && reviewMode) {
      setReviewMode(false);
    } else if (!newOpen && !reviewMode && !showCompletion) {
      if (deployment) {
        const deploymentHash = hashString(deployment);
        const newCompleted = [...completed];
        const step = relevantSteps[currentStep];
        if (!newCompleted.includes(step.id)) {
          newCompleted.push(step.id);
        }
        localStorage.setItem(
          `${deploymentHash}-cryptpad-onboarding-steps-${meta.callsign}`,
          JSON.stringify(newCompleted),
        );
        setCompleted(newCompleted);
      }
      setCanReview(true);
      toast.success(t("onboarding.progressSaved") || "Progress saved", {
        duration: 2000,
      });
    }
  };

  const handleComplete = () => {
    const step = relevantSteps[currentStep];
    if (!completed.includes(step.id)) {
      const newCompleted = [...completed, step.id];
      setCompleted(newCompleted);
      if (deployment) {
        const deploymentHash = hashString(deployment);
        localStorage.setItem(
          `${deploymentHash}-cryptpad-onboarding-steps-${meta.callsign}`,
          JSON.stringify(newCompleted),
        );
      }
    }

    if (currentStep === relevantSteps.length - 1) {
      if (deployment) {
        const deploymentHash = hashString(deployment);
        localStorage.setItem(
          `${deploymentHash}-cryptpad-onboarding-${meta.callsign}`,
          "true",
        );
      }
      setOpen(false);
      setShowCompletion(false);
      setCanReview(true);
      setReviewMode(false);
      toast.success(t("onboarding.completion"), { duration: 3000 });
    } else {
      handleNext();
    }
  };

  if (relevantSteps.length === 0) return null;
  if (isMobile === undefined) return null;

  const step = relevantSteps[currentStep];
  const progress = ((currentStep + 1) / relevantSteps.length) * 100;
  const imageUrl = getOnboardingImage(step, isMobile, false);
  const enlargedImageUrl = getOnboardingImage(step, isMobile, false);

  if (!open) {
    return (
      <button
        onClick={handleReviewClick}
        className="fixed bottom-6 right-6 p-3 rounded-full bg-primary-light hover:bg-primary-light/90 shadow-lg transition-all z-40 hover:scale-110 cursor-pointer"
        title={t("onboarding.review") || "Review onboarding"}
        aria-label={t("onboarding.review")}
      >
        <Info className="w-5 h-5" />
      </button>
    );
  }

  const contentComponent = (
    <div className="flex flex-col h-full max-h-[85vh] w-full overflow-hidden">
      <DialogTitle className="sr-only">
        {t("onboarding.title") || "What is CryptPad?"}
      </DialogTitle>
      <div className="flex-1 overflow-y-auto min-h-0 p-4 md:p-6 flex flex-col">
        <div className="flex flex-col gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold">{t(step.title)}</h2>
            </div>
            <p className="text-xs text-muted-foreground">
              {t("onboarding.step")} {currentStep + 1} {t("onboarding.of")}{" "}
              {relevantSteps.length}
            </p>
          </div>

          <div
            className={cn(
              "relative rounded-lg overflow-hidden border border-border aspect-video w-full shadow-md",
              !imageError && !imageLoading && "cursor-pointer group",
            )}
            onClick={() =>
              !imageError && !imageLoading && setImageEnlarged(true)
            }
          >
            {imageLoading && !imageError && (
              <div className="w-full h-full flex flex-col items-center justify-center bg-muted/30 text-muted-foreground">
                <div className="w-8 h-8 border-2 border-primary-light border-t-transparent rounded-full animate-spin" />
              </div>
            )}
            {imageError ? (
              <div className="w-full h-full flex flex-col items-center justify-center bg-muted/50 text-muted-foreground gap-3">
                <ImageOff className="w-12 h-12" />
                <span className="text-sm font-medium">
                  {t("onboarding.imageMissing") || "Image not available"}
                </span>
              </div>
            ) : (
              <>
                <img
                  src={imageUrl}
                  alt={t(step.title)}
                  loading="lazy"
                  className={cn(
                    "w-full h-full object-contain [image-rendering:-webkit-optimize-contrast]",
                    imageLoading && "hidden",
                  )}
                  onLoad={() => {
                    setImageLoading(false);
                    imageCache.set(imageUrl, { loaded: true, error: false });
                  }}
                  onError={() => {
                    setImageError(true);
                    setImageLoading(false);
                    imageCache.set(imageUrl, { loaded: true, error: true });
                  }}
                />
                {!imageLoading && (
                  <div className="absolute inset-0 bg-black/0 flex items-center justify-center group-hover:bg-black/10">
                    <span className="text-white text-sm font-medium opacity-0 bg-black/50 px-3 py-1 rounded-full group-hover:opacity-100">
                      {t("onboarding.clickToEnlarge") || "Click to enlarge"}
                    </span>
                  </div>
                )}
              </>
            )}
          </div>
          <p className="text-xs text-muted-foreground leading-relaxed">
            {t(step.description)}
          </p>
        </div>
      </div>

      <div className="p-4 border-t bg-background flex gap-3 shrink-0 mt-auto">
        <Button
          variant="outline"
          onClick={handlePrev}
          disabled={currentStep === 0}
          className="flex-1 cursor-pointer"
        >
          <ChevronLeft className="w-4 h-4 mr-2" /> {t("onboarding.back")}
        </Button>
        <Button
          onClick={handleComplete}
          className="flex-1 bg-primary-light hover:bg-primary-light/90 text-white cursor-pointer"
        >
          {currentStep === relevantSteps.length - 1
            ? t("onboarding.finish")
            : t("onboarding.next")}
          <ChevronRight className="w-4 h-4 ml-2" />
        </Button>
      </div>

      <div className="h-1.5 w-full bg-muted shrink-0">
        <div
          className="bg-primary-light h-2"
          style={{ width: `${progress}%` }}
        />
      </div>
    </div>
  );

  const enlargedImageModal = (
    <Dialog open={imageEnlarged} onOpenChange={setImageEnlarged}>
      <DialogContent
        className="max-w-none! w-[95vw]! h-[95vh]! p-0 bg-black/95 border-none shadow-none flex items-center justify-center"
        onClick={() => setImageEnlarged(false)}
      >
        <div className="w-full h-full flex items-center justify-center">
          <DialogTitle className="sr-only">{t(step.title)}</DialogTitle>
          <img
            src={enlargedImageUrl}
            alt={t(step.title)}
            className="w-auto h-auto max-w-[90vw] max-h-[90vh] object-contain rounded-lg shadow-2xl"
          />
        </div>
      </DialogContent>
    </Dialog>
  );

  if (isMobile) {
    return (
      <>
        {enlargedImageModal}
        <Drawer open={open} onOpenChange={handleOpenChange}>
          <DrawerContent>{contentComponent}</DrawerContent>
        </Drawer>
      </>
    );
  }

  return (
    <>
      {enlargedImageModal}
      <Dialog open={open} onOpenChange={handleOpenChange}>
        <DialogContent className="max-w-2xl max-h-[90vh] p-0 flex flex-col overflow-hidden outline-none">
          {contentComponent}
        </DialogContent>
      </Dialog>
    </>
  );
}
