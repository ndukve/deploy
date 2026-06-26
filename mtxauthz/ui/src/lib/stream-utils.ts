import { StreamConfig } from "@/model/stream-config";

export function isStreamLive(urls: StreamConfig["urls"]): boolean {
  return Object.values(urls).some((url) => url);
}

export function parseStreamPath(path: string) {
  const segments = path.split("/").filter(Boolean);
  return {
    name: segments[segments.length - 1] ?? path,
    category: segments.length > 1 ? segments.slice(0, -1).join(" / ") : null,
  };
}

export function streamPathToSlug(path: string): string {
  return path.replaceAll("/", "-");
}

export function getBaseDomain(): string {
  return window.location.hostname.replace(/^mtls\./, "");
}

export function maskStreamUrl(
  url: string,
  password: string,
  passphrase?: string,
): string {
  let masked = url.replaceAll(password, "***");
  if (passphrase) masked = masked.replaceAll(passphrase, "***");
  return masked;
}
