export enum Platform {
  Android = "android",
  iOS = "ios",
  Windows = "windows",
  Tracker = "tracker",
}

export const detectPlatform = (): Platform => {
  if (typeof window === "undefined") return Platform.Android;

  const navWithOpera = window as Window & { opera?: string };
  const ua: string =
    window.navigator.userAgent ||
    window.navigator.vendor ||
    navWithOpera.opera ||
    "";

  if (/android/i.test(ua)) return Platform.Android;
  if (/iPad|iPhone|iPod/.test(ua)) return Platform.iOS;
  if (/Windows NT/.test(ua)) return Platform.Windows;

  return Platform.Android;
};
