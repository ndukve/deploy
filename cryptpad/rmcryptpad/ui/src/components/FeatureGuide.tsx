import { useState, useCallback, useEffect } from "react";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { PRODUCT_SHORTNAME } from "@/App";
import { Button } from "@/components/ui/button";
import { ChevronRight, ChevronLeft, ImageOff } from "lucide-react";
import { useIsMobile } from "@/hooks/use-mobile";
import { useTranslation } from "react-i18next";
import { cn } from "@/lib/utils";

interface FeatureStep {
  id: string;
  title: string;
  description: string;
  image: string;
  mobileImage?: string;
}

interface FeatureGuideProps {
  featureKey: string;
  steps: FeatureStep[];
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const imageCache = new Map<string, { loaded: boolean; error: boolean }>();

export function FeatureGuide({
  featureKey,
  steps,
  open,
  onOpenChange,
}: FeatureGuideProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [imageEnlarged, setImageEnlarged] = useState(false);
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);
  const isMobile = useIsMobile();
  const { t } = useTranslation(PRODUCT_SHORTNAME);

  const getImage = useCallback(
    (step: FeatureStep) => {
      return isMobile && step.mobileImage ? step.mobileImage : step.image;
    },
    [isMobile],
  );

  // Preload the next step's image so it's ready before the user clicks Next
  useEffect(() => {
    if (currentStep < steps.length - 1) {
      const nextUrl = getImage(steps[currentStep + 1]);
      if (!imageCache.has(nextUrl)) {
        const img = new Image();
        img.onload = () =>
          imageCache.set(nextUrl, { loaded: true, error: false });
        img.onerror = () =>
          imageCache.set(nextUrl, { loaded: true, error: true });
        img.src = nextUrl;
      }
    }
  }, [currentStep, steps, getImage]);

  const goToStep = (index: number) => {
    const url = getImage(steps[index]);
    const cached = imageCache.get(url);
    setCurrentStep(index);
    setImageError(cached?.error ?? false);
    setImageLoading(!cached);
  };

  const handleNext = () => {
    if (currentStep < steps.length - 1) goToStep(currentStep + 1);
  };

  const handlePrev = () => {
    if (currentStep > 0) goToStep(currentStep - 1);
  };

  const handleFinish = () => {
    onOpenChange(false);
    setCurrentStep(0);
  };

  const handleOpenChange = (newOpen: boolean) => {
    onOpenChange(newOpen);
    if (!newOpen) {
      setCurrentStep(0);
    }
  };

  if (steps.length === 0 || isMobile === undefined) return null;

  const step = steps[currentStep];
  const progress = ((currentStep + 1) / steps.length) * 100;
  const imageUrl = getImage(step);

  const contentComponent = (
    <div className="flex flex-col h-full max-h-[85vh] w-full overflow-hidden">
      <DialogTitle className="sr-only">
        {t(`features.${featureKey}.title`)}
      </DialogTitle>
      <div className="flex-1 overflow-y-auto min-h-0 p-4 md:p-6 flex flex-col">
        <div className="flex flex-col gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold">{t(step.title)}</h2>
            </div>
            <p className="text-xs text-muted-foreground">
              {t("onboarding.step")} {currentStep + 1} {t("onboarding.of")}{" "}
              {steps.length}
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
          onClick={currentStep === steps.length - 1 ? handleFinish : handleNext}
          className="flex-1 bg-primary-light hover:bg-primary-light/90 text-white cursor-pointer"
        >
          {currentStep === steps.length - 1
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
            src={imageUrl}
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
