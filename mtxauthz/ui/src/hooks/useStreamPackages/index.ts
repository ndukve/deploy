import { useCallback, useMemo } from "react";
import {
  StreamPackageParams,
  getAtakRtmps,
  getBrowserHls,
  getVlcHls,
  getVlcSrt,
} from "./packages";
import { useCredentials } from "@/hooks/useCredentials";
import { useSrtPasswords } from "@/hooks/useSrtPasswords";
import useHealthCheck from "@/hooks/helpers/useHealthcheck";
import { getBaseDomain } from "@/lib/stream-utils";

function downloadFile(content: string, filename: string, mimeType: string) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function sanitizeFilename(streamPath: string) {
  return streamPath.replace(/^\//, "").replace(/\//g, "_");
}

export function useStreamPackages(streamPath: string) {
  const currentDomain = useMemo(() => getBaseDomain(), []);
  const { data: credentials } = useCredentials();
  const { data: srtPasswords } = useSrtPasswords();
  const { deployment } = useHealthCheck();
  const filenamePrefix = deployment ? `${deployment}_` : "";

  const params: StreamPackageParams | null =
    credentials && srtPasswords
      ? {
          streamPath,
          currentDomain,
          username: credentials.username,
          password: credentials.password,
          srtReadPassphrase: srtPasswords.read,
        }
      : null;

  const stableParams = useMemo(
    () => params,
    [
      params?.streamPath,
      params?.currentDomain,
      params?.username,
      params?.password,
      params?.srtReadPassphrase,
    ],
  );

  const downloadAtakRtmps = useCallback(() => {
    if (!stableParams) return;
    const content = getAtakRtmps(stableParams);
    const filename = `${filenamePrefix}atak-rtmps-${sanitizeFilename(
      stableParams.streamPath,
    )}.xml`;
    downloadFile(content, filename, "application/xml");
  }, [stableParams, filenamePrefix]);

  const downloadBrowserHls = useCallback(() => {
    if (!stableParams) return;
    const content = getBrowserHls(stableParams);
    const filename = `${filenamePrefix}browser-hls-${sanitizeFilename(
      stableParams.streamPath,
    )}.htm`;
    downloadFile(content, filename, "text/html");
  }, [stableParams, filenamePrefix]);

  const downloadVlcSrt = useCallback(() => {
    if (!stableParams) return;
    const content = getVlcSrt(stableParams);
    const filename = `${filenamePrefix}vlc-srt-${sanitizeFilename(
      stableParams.streamPath,
    )}.m3u`;
    downloadFile(content, filename, "application/xml");
  }, [stableParams, filenamePrefix]);

  const downloadVlcHls = useCallback(() => {
    if (!stableParams) return;
    const content = getVlcHls(stableParams);
    const filename = `${filenamePrefix}vlc-hls-${sanitizeFilename(
      stableParams.streamPath,
    )}.m3u8`;
    downloadFile(content, filename, "text/html");
  }, [stableParams, filenamePrefix]);

  return {
    downloadAtakRtmps,
    downloadBrowserHls,
    downloadVlcHls,
    downloadVlcSrt,
    ready: stableParams !== null,
  };
}
