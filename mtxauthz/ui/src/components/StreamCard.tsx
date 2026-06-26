import {
  Monitor,
  Globe,
  Crosshair,
  LucideIcon,
  TrafficCone,
} from "lucide-react";
import { useTranslation } from "react-i18next";
import { PRODUCT_SHORTNAME } from "@/App";
import { Card } from "@/components/ui/card";
import { StreamConfig } from "@/model/stream-config";
import { parseStreamPath } from "@/lib/stream-utils";

interface StreamCardProps {
  stream: StreamConfig;
  onClick: () => void;
}

export function StreamCard({ stream, onClick }: StreamCardProps) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const { name, category } = parseStreamPath(stream.path);
  const availableProtocols = Object.entries(stream.urls)
    .filter(([, url]) => url)
    .map(([protocol]) => protocol.toUpperCase());

  const methods: { label: string; icon: LucideIcon }[] = [];
  if (stream.urls.hls)
    methods.push({ label: t("video.downloadBrowser"), icon: Globe });
  if (stream.urls.srt)
    methods.push({ label: t("video.downloadVlc"), icon: TrafficCone });
  if (stream.urls.rtmps)
    methods.push({ label: t("video.downloadTak"), icon: Crosshair });

  return (
    <button
      onClick={onClick}
      className="text-left w-full focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded-lg"
    >
      <Card className="overflow-hidden hover:border-primary hover:shadow-lg hover:-translate-y-1 transition-all duration-300 gap-0 py-0">
        <div className="aspect-video bg-muted flex items-center justify-center">
          <Monitor className="w-8 h-8 text-muted-foreground" />
        </div>
        <div className="px-3 py-2">
          <p className="font-semibold text-foreground text-sm truncate">
            {name}
          </p>
          {category && (
            <p className="text-xs text-muted-foreground truncate mt-0.5">
              {category}
            </p>
          )}
          <div className="flex gap-1 mt-2 flex-wrap">
            {methods.map(({ label, icon: Icon }) => (
              <span
                key={label}
                className="inline-flex items-center gap-1 text-xs bg-primary/10 text-foreground px-1.5 py-0.5 rounded"
              >
                <Icon className="w-3 h-3" aria-hidden="true" />
                {label}
              </span>
            ))}
            {availableProtocols.length > 0 && (
              <span
                className="text-xs bg-primary/10 text-foreground px-1.5 py-0.5 rounded"
                title={availableProtocols.join(", ")}
              >
                +{availableProtocols.length}
              </span>
            )}
          </div>
        </div>
      </Card>
    </button>
  );
}
