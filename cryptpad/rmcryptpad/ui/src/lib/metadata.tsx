import { createContext, useContext, ReactNode, useMemo } from "react";

export interface CryptPadCardData {
  url: string;
  sandbox_url: string;
}

export interface MetaData {
  theme: string;
  callsign: string;
}

const MetaContext = createContext<MetaData | undefined>(undefined);

export const MetaProvider = ({
  children,
  meta,
}: {
  children: ReactNode;
  meta: MetaData;
}) => {
  const value = useMemo(() => meta, [meta]);

  return <MetaContext.Provider value={value}>{children}</MetaContext.Provider>;
};

export const useMeta = () => {
  const context = useContext(MetaContext);
  if (context === undefined) {
    throw new Error("useMeta must be used within a MetaProvider");
  }
  return context;
};

export function buildLoginUrl(url: string): string {
  try {
    return new URL("/login/", url).toString();
  } catch {
    return `${url.replace(/\/+$/, "")}/login/`;
  }
}
