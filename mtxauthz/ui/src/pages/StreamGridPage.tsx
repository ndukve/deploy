import { useMemo, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Search, AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import { PRODUCT_SHORTNAME } from "@/App";
import { StreamConfig } from "@/model/stream-config";
import { StreamCard } from "@/components/StreamCard";
import { Button } from "@/components/ui/button";
import {
  InputGroup,
  InputGroupInput,
  InputGroupAddon,
} from "@/components/ui/input-group";
import { useStreams } from "@/hooks/useStreams";
import { streamPathToSlug } from "@/lib/stream-utils";

interface StreamGridPageProps {
  onStartBroadcast: () => void;
}

export function StreamGridPage({ onStartBroadcast }: StreamGridPageProps) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const navigate = useNavigate();
  const [search, setSearch] = useState("");

  const { data: streams = [], isLoading, error, refetch } = useStreams();

  const filtered = useMemo(() => {
    const s = search.toLowerCase();
    if (!s) return streams;
    return streams.filter((item) => item.path.toLowerCase().includes(s));
  }, [search, streams]);

  const handleStreamClick = (stream: StreamConfig) => {
    void navigate({ to: `/${streamPathToSlug(stream.path)}` });
  };

  if (isLoading) {
    return (
      <div className="space-y-6" role="status" aria-busy="true">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1 h-10 bg-muted animate-pulse rounded-md" />
          <div className="h-10 w-40 bg-muted animate-pulse rounded-md" />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-lg overflow-hidden">
              <div className="aspect-video bg-muted animate-pulse" />
              <div className="p-3 space-y-2">
                <div className="h-4 bg-muted animate-pulse rounded w-3/4" />
                <div className="h-3 bg-muted animate-pulse rounded w-1/2" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error && streams.length === 0) {
    return (
      <div
        className="flex flex-col items-center justify-center py-16 space-y-4"
        role="alert"
      >
        <AlertCircle className="w-12 h-12 text-muted-foreground" />
        <p className="text-lg font-semibold text-foreground">
          {t("streams.errorLoading")}
        </p>
        <Button
          onClick={() => {
            void refetch();
          }}
        >
          {t("common.retry")}
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {error && streams.length > 0 && (
        <div
          className="flex items-center gap-2 p-3 rounded-md bg-destructive/10 text-destructive text-sm"
          role="alert"
        >
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>{t("streams.errorLoadingStale")}</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              void refetch();
            }}
            className="ml-auto"
          >
            {t("common.retry")}
          </Button>
        </div>
      )}

      <div>
        <h1 className="text-xl md:text-2xl font-bold text-foreground">
          MediaMTX
        </h1>
        <p className="text-sm text-muted-foreground mt-1">
          {t("home.description")}
        </p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <InputGroup className="flex-1">
          <InputGroupInput
            placeholder={t("home.search")}
            aria-label={t("home.search")}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <InputGroupAddon>
            <Search aria-hidden="true" />
          </InputGroupAddon>
          <InputGroupAddon align="inline-end">
            {filtered.length}{" "}
            {filtered.length === 1 ? t("home.result") : t("home.results")}
          </InputGroupAddon>
        </InputGroup>
        <Button onClick={onStartBroadcast}>
          {t("streams.startBroadcasting")}
        </Button>
      </div>

      {streams.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <p className="text-lg font-semibold text-foreground">
            {t("streams.noStreams")}
          </p>
          <p className="text-sm text-muted-foreground">
            {t("streams.noStreamsHint")}
          </p>
          <Button onClick={onStartBroadcast}>
            {t("streams.startBroadcasting")}
          </Button>
        </div>
      )}

      {streams.length > 0 && filtered.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <p className="text-foreground">
            {t("streams.noSearchResults", { query: search })}
          </p>
          <Button variant="ghost" onClick={() => setSearch("")}>
            {t("streams.clearSearch")}
          </Button>
        </div>
      )}

      {filtered.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filtered.map((stream) => (
            <StreamCard
              key={stream.path}
              stream={stream}
              onClick={() => handleStreamClick(stream)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
