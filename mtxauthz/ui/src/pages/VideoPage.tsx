import { useState, useMemo, useEffect, useRef } from "react";
import { useNavigate } from "@tanstack/react-router";
import { ArrowLeft, Monitor, Play, Settings, AlertCircle } from "lucide-react";
import { useTranslation } from "react-i18next";
import Hls from "hls.js";
import { PRODUCT_SHORTNAME } from "@/App";
import { Button } from "@/components/ui/button";
import { ConnectionOptionsDialog } from "@/components/ConnectionOptionsDialog";
import { useStreams } from "@/hooks/useStreams";
import { useCredentials } from "@/hooks/useCredentials";
import {
  isStreamLive,
  parseStreamPath,
  streamPathToSlug,
} from "@/lib/stream-utils";

function toPlaylistUrl(rawUrl: string): string {
  const u = new URL(rawUrl);
  u.username = "";
  u.password = "";
  if (!u.pathname.endsWith(".m3u8")) {
    u.pathname = u.pathname.replace(/\/+$/, "") + "/index.m3u8";
  }
  return u.toString();
}

interface VideoPageProps {
  streamSlug: string;
}

export function VideoPage({ streamSlug }: VideoPageProps) {
  const { t } = useTranslation(PRODUCT_SHORTNAME);
  const navigate = useNavigate();
  const [playing, setPlaying] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [playbackError, setPlaybackError] = useState(false);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  const { data: streams = [], isLoading: streamsLoading } = useStreams();
  const { data: credentials, error: credentialsError } = useCredentials();

  const stream = useMemo(
    () => streams.find((s) => streamPathToSlug(s.path) === streamSlug),
    [streams, streamSlug],
  );

  const live = stream ? isStreamLive(stream.urls) : false;
  const streamPath = stream?.path ?? streamSlug.replaceAll("-", "/");
  const { name: streamName } = parseStreamPath(streamPath);

  const hlsUrl = stream?.urls.hls;
  const username = credentials?.username;
  const password = credentials?.password;

  useEffect(() => {
    if (!playing || !hlsUrl || !username || !password) return;
    const video = videoRef.current;
    if (!video) return;

    setPlaybackError(false);

    if (Hls.isSupported()) {
      const playlistUrl = toPlaylistUrl(hlsUrl);
      const authHeader = "Basic " + btoa(`${username}:${password}`);
      const retryPolicy = {
        default: {
          maxTimeToFirstByteMs: 10000,
          maxLoadTimeMs: 100000,
          timeoutRetry: {
            maxNumRetry: 4,
            retryDelayMs: 0,
            maxRetryDelayMs: 0,
          },
          errorRetry: {
            maxNumRetry: 8,
            retryDelayMs: 1000,
            maxRetryDelayMs: 8000,
            backoff: "exponential" as const,
          },
        },
      };

      const hls = new Hls({
        xhrSetup: (xhr) => {
          xhr.setRequestHeader("Authorization", authHeader);
        },
        manifestLoadPolicy: retryPolicy,
        playlistLoadPolicy: retryPolicy,
        fragLoadPolicy: retryPolicy,
      });

      let attemptedErrorRecovery: number | null = null;
      const RECOVERY_THROTTLE_MS = 5000;

      const tryRecoverMediaError = () => {
        const now = Date.now();
        if (
          !attemptedErrorRecovery ||
          now - attemptedErrorRecovery > RECOVERY_THROTTLE_MS
        ) {
          attemptedErrorRecovery = now;
          hls.recoverMediaError();
          return true;
        }
        return false;
      };

      const handleVideoError = () => {
        const mediaError = video.error;
        if (mediaError && mediaError.code === mediaError.MEDIA_ERR_DECODE) {
          tryRecoverMediaError();
        }
      };
      video.addEventListener("error", handleVideoError);

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        video.play().catch(() => {});
      });
      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (!data.fatal) return;
        switch (data.type) {
          case Hls.ErrorTypes.MEDIA_ERROR:
            if (!tryRecoverMediaError()) {
              setPlaybackError(true);
              hls.destroy();
            }
            break;

          default:
            setPlaybackError(true);
            hls.destroy();
            break;
        }
      });
      hls.loadSource(playlistUrl);
      hls.attachMedia(video);
      return () => {
        video.removeEventListener("error", handleVideoError);
        hls.destroy();
      };
    }

    if (video.canPlayType("application/vnd.apple.mpegurl")) {
      video.src = hlsUrl;
      video.play().catch(() => {});
      return () => {
        video.removeAttribute("src");
        video.load();
      };
    }

    setPlaybackError(true);
  }, [playing, hlsUrl, username, password]);

  const goBack = () => {
    void navigate({ to: "/" });
  };

  const backLink = (
    <button
      onClick={goBack}
      aria-label={t("video.backToStreams")}
      className="inline-flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring rounded transition-colors"
    >
      <ArrowLeft className="w-4 h-4" />
      {t("video.backToStreams")}
    </button>
  );

  if (streamsLoading) {
    return (
      <div className="space-y-6" role="status" aria-busy="true">
        <div className="h-5 w-32 bg-muted animate-pulse rounded" />
        <div className="h-8 w-64 bg-muted animate-pulse rounded" />
        <div className="aspect-video bg-muted animate-pulse rounded-lg" />
      </div>
    );
  }

  if (!stream) {
    return (
      <div className="space-y-6">
        {backLink}
        <div className="aspect-video bg-muted rounded-lg flex flex-col items-center justify-center space-y-4">
          <AlertCircle className="w-12 h-12 text-muted-foreground" />
          <p className="text-lg font-semibold text-foreground">
            {t("video.streamNotFound")}
          </p>
          <p className="text-sm text-muted-foreground">
            {t("video.streamNotFoundHint")}
          </p>
          <Button onClick={goBack}>{t("video.backToStreams")}</Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {backLink}

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div className="min-w-0 max-w-full">
          <h1 className="text-xl md:text-2xl font-bold text-foreground truncate">
            {streamName}
          </h1>
          <p className="text-sm text-muted-foreground mt-1 truncate">
            {streamPath}
          </p>
        </div>
        <Button
          variant="outline"
          size="sm"
          onClick={() => setDialogOpen(true)}
          className="shrink-0"
        >
          <Settings className="w-4 h-4 mr-2" />
          {t("video.connectionOptions")}
        </Button>
      </div>

      <div
        className="w-full bg-muted rounded-lg overflow-hidden"
        style={{
          aspectRatio: "16/9",
          minHeight: "200px",
          maxHeight: "calc(100dvh - 14rem)",
        }}
      >
        {playing && hlsUrl && !playbackError ? (
          <video
            ref={videoRef}
            controls
            playsInline
            autoPlay
            className="w-full h-full bg-black"
            title={streamName}
          />
        ) : playing && playbackError ? (
          <div className="w-full h-full flex flex-col items-center justify-center space-y-3">
            <AlertCircle className="w-12 h-12 text-muted-foreground" />
            <p className="text-foreground font-semibold">
              {t("video.playbackError")}
            </p>
            <p className="text-sm text-muted-foreground">
              {t("video.playbackErrorHint")}
            </p>
          </div>
        ) : !live ? (
          <div className="w-full h-full flex flex-col items-center justify-center space-y-3">
            <Monitor className="w-12 h-12 text-muted-foreground" />
            <p className="text-foreground font-semibold">
              {t("video.streamOffline")}
            </p>
            <p className="text-sm text-muted-foreground">
              {t("video.streamOfflineHint")}
            </p>
          </div>
        ) : (
          <button
            onClick={() => setPlaying(true)}
            disabled={!credentials}
            aria-label={t("video.play")}
            className="w-full h-full flex flex-col items-center justify-center space-y-3 cursor-pointer hover:bg-muted/80 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-inset transition-colors disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:bg-muted"
          >
            <Monitor className="w-12 h-12 text-muted-foreground" />
            <div className="w-16 h-16 rounded-full bg-primary/90 flex items-center justify-center">
              <Play className="w-8 h-8 text-primary-foreground ml-1" />
            </div>
            <p className="text-sm text-muted-foreground">{t("video.play")}</p>
          </button>
        )}
      </div>

      <ConnectionOptionsDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        stream={stream}
        credentials={credentials ?? null}
        credentialsError={!!credentialsError}
      />
    </div>
  );
}
