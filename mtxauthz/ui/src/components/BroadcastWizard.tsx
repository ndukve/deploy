import { useState, type ReactNode } from "react";
import { ArrowLeft, Copy, Eye, EyeClosed, ExternalLink } from "lucide-react";
import { useTranslation } from "react-i18next";
import { PRODUCT_SHORTNAME } from "@/App";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { copyToClipboard } from "@/lib/clipboard";
import { useIsMobile } from "@/hooks/use-mobile";
import { Drawer, DrawerContent } from "@/components/ui/drawer";
import { useCredentials } from "@/hooks/useCredentials";
import { useSrtPasswords } from "@/hooks/useSrtPasswords";
import { getBaseDomain, maskStreamUrl } from "@/lib/stream-utils";
import { Credentials, SrtPasswords } from "@/model/stream-config";

type Tool = "opentak_icu" | "gopro" | "uastool" | "advanced";

interface BroadcastWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const TOOLS: { id: Tool; nameKey: string; descKey: string }[] = [
  {
    id: "opentak_icu",
    nameKey: "broadcast.opentak_icu",
    descKey: "broadcast.opentak_icu_desc",
  },
  { id: "gopro", nameKey: "broadcast.gopro", descKey: "broadcast.gopro_desc" },
  {
    id: "uastool",
    nameKey: "broadcast.uastool",
    descKey: "broadcast.uastool_desc",
  },
  {
    id: "advanced",
    nameKey: "broadcast.advanced",
    descKey: "broadcast.advanced_desc",
  },
];

export function BroadcastWizard({ open, onOpenChange }: BroadcastWizardProps) {
  const isMobile = useIsMobile();

  if (isMobile) {
    return (
      <Drawer open={open} onOpenChange={onOpenChange}>
        <DrawerContent className="max-h-[85dvh]">
          <div className="overflow-y-auto p-4">
            <WizardContent />
          </div>
        </DrawerContent>
      </Drawer>
    );
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md max-h-[85dvh] overflow-y-auto">
        <WizardContent />
      </DialogContent>
    </Dialog>
  );
}

function WizardContent() {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const [step, setStep] = useState<"select" | "guide">("select");
  const [selectedTool, setSelectedTool] = useState<Tool | null>(null);

  const currentDomain = getBaseDomain();
  const { data: credentials, error: credentialsError } = useCredentials();
  const { data: srtPasswords } = useSrtPasswords();

  const handleSelectTool = (tool: Tool) => {
    setSelectedTool(tool);
    setStep("guide");
  };

  if (step === "select") {
    return (
      <>
        <DialogHeader className="pb-3">
          <DialogTitle>{t("broadcast.title")}</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          {t("broadcast.selectTool")}
        </p>
        <div className="space-y-2 mt-2">
          {TOOLS.map((tool) => (
            <button
              key={tool.id}
              onClick={() => handleSelectTool(tool.id)}
              className="w-full text-left p-3 rounded-lg border border-border hover:border-primary hover:bg-primary/5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring transition-colors"
            >
              <p className="font-semibold text-foreground text-sm">
                {t(tool.nameKey)}
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                {t(tool.descKey)}
              </p>
            </button>
          ))}
        </div>
      </>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <button
          onClick={() => setStep("select")}
          aria-label={t("common.back")}
          className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded transition-colors mb-3"
        >
          <ArrowLeft className="w-4 h-4" />
          {t("common.back")}
        </button>
        <DialogHeader className="pb-3">
          <DialogTitle>
            {TOOLS.find((tool) => tool.id === selectedTool)
              ? t(TOOLS.find((tool) => tool.id === selectedTool)!.nameKey)
              : ""}
          </DialogTitle>
        </DialogHeader>
      </div>

      {credentialsError && (
        <p className="text-destructive text-sm" role="alert">
          {t("video.credentialsError")}
        </p>
      )}

      {credentials && selectedTool === "opentak_icu" && (
        <OpenTakIcuGuide credentials={credentials} domain={currentDomain} />
      )}
      {credentials && selectedTool === "gopro" && (
        <GoProGuide credentials={credentials} domain={currentDomain} />
      )}
      {credentials && selectedTool === "uastool" && (
        <UasToolGuide
          credentials={credentials}
          domain={currentDomain}
          srtPasswords={srtPasswords ?? null}
        />
      )}
      {credentials && selectedTool === "advanced" && (
        <AdvancedGuide
          credentials={credentials}
          domain={currentDomain}
          srtPasswords={srtPasswords ?? null}
        />
      )}
    </div>
  );
}

function StepList({ steps }: { steps: ReactNode[] }) {
  return (
    <ol className="space-y-4 text-sm text-foreground">
      {steps.map((step, i) => (
        <li key={i} className="flex gap-4 items-start">
          <span className="shrink-0 w-7 h-7 rounded-full bg-muted flex items-center justify-center text-xs font-semibold text-muted-foreground">
            {i + 1}
          </span>
          <div className="flex-1 leading-7">{step}</div>
        </li>
      ))}
    </ol>
  );
}

const STORE_BADGE_LOCALES = ["en", "fi", "sv"] as const;
type StoreBadgeLocale = (typeof STORE_BADGE_LOCALES)[number];

function GoProStoreBadges() {
  const { t, i18n } = useTranslation(PRODUCT_SHORTNAME);
  const lang = (STORE_BADGE_LOCALES as readonly string[]).includes(
    i18n.language,
  )
    ? (i18n.language as StoreBadgeLocale)
    : "en";

  return (
    <div className="flex flex-wrap items-center gap-3 mt-2">
      <a
        href="https://apps.apple.com/fi/app/gopro-quik/id561350520"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block"
      >
        <img
          src={`/ui/mtx/assets/appstore/${lang}.svg`}
          alt={t("broadcast.gopro_appstore_alt")}
          className="h-12 w-auto"
        />
      </a>
      <a
        href="https://play.google.com/store/apps/details?id=com.gopro.smarty"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block"
      >
        <img
          src={`/ui/mtx/assets/googleplay/${lang}.svg`}
          alt={t("broadcast.gopro_googleplay_alt")}
          className="h-12 w-auto"
        />
      </a>
    </div>
  );
}

function UasToolStoreBadge() {
  const { t, i18n } = useTranslation(PRODUCT_SHORTNAME);
  const lang = (STORE_BADGE_LOCALES as readonly string[]).includes(
    i18n.language,
  )
    ? (i18n.language as StoreBadgeLocale)
    : "en";

  return (
    <div className="flex flex-wrap items-center gap-3 mt-2">
      <a
        href="https://play.google.com/store/apps/details?id=com.atakmap.android.uastool.plugin"
        target="_blank"
        rel="noopener noreferrer"
        className="inline-block"
      >
        <img
          src={`/ui/mtx/assets/googleplay/${lang}.svg`}
          alt={t("broadcast.uastool_googleplay_alt")}
          className="h-12 w-auto"
        />
      </a>
    </div>
  );
}

function GuideLink({ toolKey }: { toolKey: Exclude<Tool, "advanced"> }) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const guideUrl = t(`broadcast.${toolKey}_guide_url`);

  return (
    <div className="pt-3 border-t border-border">
      <a
        href={guideUrl}
        target="_blank"
        rel="noopener noreferrer"
        className="flex items-center gap-3 p-3 rounded-lg border border-border hover:border-primary hover:bg-primary/5 transition-colors"
      >
        <ExternalLink className="w-5 h-5 text-muted-foreground shrink-0" />
        <div className="min-w-0">
          <p className="text-sm font-semibold text-foreground">
            {t(`broadcast.${toolKey}_guide`)}
          </p>
          <p className="text-xs text-muted-foreground mt-0.5">
            {t("broadcast.guideHint")}
          </p>
        </div>
      </a>
    </div>
  );
}

function OpenTakIcuGuide({
  credentials,
  domain,
}: {
  credentials: Credentials;
  domain: string;
}) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);

  const openTakIcuUrl = (() => {
    const params = new URLSearchParams();
    params.append("protocol", "rtmps");
    params.append("address", domain);
    params.append("port", "1936");
    params.append("path", `/live/icu/${credentials.username}`);
    params.append("username", credentials.username);
    params.append("password", credentials.password);
    return `opentakicu://import?${params.toString()}`;
  })();

  return (
    <div className="flex flex-col gap-6">
      <div className="pt-2">
        <a href={openTakIcuUrl} target="_blank" rel="noopener noreferrer">
          <Button className="w-full">{t("broadcast.importSettings")}</Button>
        </a>
      </div>

      <StepList
        steps={[
          t("broadcast.opentak_icu_step1"),
          t("broadcast.opentak_icu_step2"),
          t("broadcast.opentak_icu_step3"),
        ]}
      />

      <GuideLink toolKey="opentak_icu" />
    </div>
  );
}

function GoProGuide({
  credentials,
  domain,
}: {
  credentials: Credentials;
  domain: string;
}) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const [showUrl, setShowUrl] = useState(false);

  const url = `rtmps://${domain}:1936/live/gopro/${credentials.username}?user=${credentials.username}&pass=${credentials.password}`;

  return (
    <div className="space-y-4">
      <div className="flex gap-2">
        <Input
          readOnly
          type={showUrl ? "text" : "password"}
          value={url}
          className="flex-1"
        />
        <Button
          size="sm"
          variant="outline"
          aria-label={showUrl ? t("common.hide") : t("common.show")}
          onClick={() => setShowUrl(!showUrl)}
        >
          {showUrl ? (
            <EyeClosed className="w-4 h-4" />
          ) : (
            <Eye className="w-4 h-4" />
          )}
        </Button>
        <Button
          size="sm"
          aria-label={t("common.copy")}
          onClick={() => copyToClipboard(url, t("common.copied"))}
        >
          <Copy className="w-4 h-4" />
        </Button>
      </div>

      <StepList
        steps={[
          <div className="flex flex-col gap-1">
            <span>{t("broadcast.gopro_step1")}</span>
            <GoProStoreBadges />
          </div>,
          t("broadcast.gopro_step2"),
          t("broadcast.gopro_step3"),
        ]}
      />

      <GuideLink toolKey="gopro" />
    </div>
  );
}

function UasToolGuide({
  credentials,
  domain,
  srtPasswords,
}: {
  credentials: Credentials;
  domain: string;
  srtPasswords: SrtPasswords | null;
}) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);

  const uasToolUrl = (() => {
    const callsign = credentials.username;
    const readOnlyPassword = credentials.stream_ro_password;
    const params: Record<string, string> = {
      key1: "uastool.ROUTES_WAYPOINTS_OVERLAY",
      type1: "boolean",
      value1: "true",
      key2: "uastool.pref_callsign",
      type2: "string",
      value2: `UAS-${callsign}`,
      key3: "uastool.pref_poi_id_template",
      type3: "string",
      value3: "%-POI",
      key4: "uastool.pref_ui_ar_on",
      type4: "boolean",
      value4: "true",
      key5: "uastool.pref_ui_dont_show_warning",
      type5: "boolean",
      value5: "true",
      key6: "uastool.fov_use_dted",
      type6: "boolean",
      value6: "true",
      key7: "uastool.pref_cot_broadcast",
      type7: "boolean",
      value7: "true",
      key8: "uastool.pref_broadcast_ssl",
      type8: "boolean",
      value8: "true",
      key9: "uastool.pref_broadcast_size",
      type9: "string",
      value9: "1920x1080 (high)",
      key10: "uastool.pref_video_broadcast_bitrate",
      type10: "string",
      value10: "10000",
      key11: "uastool.pref_video_broadcast_destination",
      type11: "string",
      value11: "SRT (Video Management System)",
      key12: "uastool.pref_srt_dest_host",
      type12: "string",
      value12: domain,
      key13: "uastool.pref_srt_dest_port",
      type13: "string",
      value13: "8890",
      key14: "uastool.pref_srt_stream_id",
      type14: "string",
      value14: `publish:live/uas/${callsign}:${credentials.username}:${credentials.password}`,
      key15: "uastool.pref_video_observer_url",
      type15: "string",
      value15: `rtmps://${domain}:1936/live/uas/${callsign}?user=${credentials.username}&pass=${readOnlyPassword}`,
      ...(srtPasswords
        ? {
            key16: "uastool.pref_srt_passphrase",
            type16: "string",
            value16: srtPasswords.publish,
          }
        : {}),
    };
    return `tak://com.atakmap.app/preference?${new URLSearchParams(
      params,
    ).toString()}`;
  })();

  return (
    <div className="flex flex-col gap-6">
      <div className="pt-2">
        <a href={uasToolUrl}>
          <Button className="w-full">{t("broadcast.importSettings")}</Button>
        </a>
      </div>

      <StepList
        steps={[
          <div className="flex flex-col gap-1">
            <span>{t("broadcast.uastool_step1")}</span>
            <UasToolStoreBadge />
          </div>,
          t("broadcast.uastool_step2"),
          t("broadcast.uastool_step3"),
        ]}
      />

      <GuideLink toolKey="uastool" />
    </div>
  );
}

function AdvancedGuide({
  credentials,
  domain,
  srtPasswords,
}: {
  credentials: Credentials;
  domain: string;
  srtPasswords: SrtPasswords | null;
}) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);

  const srtPassphrase = srtPasswords?.publish
    ? `&passphrase=${srtPasswords.publish}`
    : "";
  const links = [
    {
      name: t("stream.rtsps"),
      url: `rtsps://${domain}:8322/live/icu/${credentials.username}`,
    },
    {
      name: t("stream.rtsps_with_auth"),
      url: `rtsps://${credentials.username}:${credentials.password}@${domain}:8322/live/icu/${credentials.username}`,
    },
    {
      name: t("stream.rtmps"),
      url: `rtmps://${domain}:1936/live/icu/${credentials.username}`,
    },
    {
      name: t("stream.rtmps_with_auth"),
      url: `rtmps://${credentials.username}:${credentials.password}@${domain}:1936/live/icu/${credentials.username}`,
    },
    {
      name: t("stream.srt"),
      url: `srt://${domain}:8890?streamid=publish:live/icu/${credentials.username}&pkt_size=1316`,
    },
    {
      name: t("stream.srt_with_auth"),
      url: `srt://${domain}:8890?streamid=publish:live/icu/${credentials.username}:${credentials.username}:${credentials.password}${srtPassphrase}&pkt_size=1316`,
    },
  ];

  return (
    <div className="space-y-2">
      {links.map((link, idx) => (
        <div
          key={idx}
          className="flex items-center justify-between gap-2 p-2 bg-muted rounded-md"
        >
          <div className="min-w-0">
            <span className="text-sm font-semibold text-foreground">
              {link.name}
            </span>
            <p className="text-xs text-muted-foreground font-mono break-all mt-0.5">
              {maskStreamUrl(
                link.url,
                credentials.password,
                srtPasswords?.publish,
              )}
            </p>
          </div>
          <Button
            variant="ghost"
            size="icon-sm"
            className="shrink-0"
            aria-label={`${t("common.copy")} ${link.name}`}
            onClick={() => copyToClipboard(link.url, t("common.copied"))}
          >
            <Copy className="w-4 h-4" />
          </Button>
        </div>
      ))}
    </div>
  );
}
