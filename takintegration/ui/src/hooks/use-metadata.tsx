import { createContext, useContext, ReactNode, useMemo } from "react";

export interface MetaData {
  theme: string;
  callsign: string;
}

const MetaContext = createContext<MetaData | undefined>(undefined);

export const MetadataProvider = ({
  children,
  meta,
}: {
  children: ReactNode;
  meta: MetaData;
}) => {
  const value = useMemo(() => meta, [meta]);

  return <MetaContext.Provider value={value}>{children}</MetaContext.Provider>;
};

export const useMetadata = () => {
  const context = useContext(MetaContext);
  if (context === undefined) {
    throw new Error("useMetadata must be used within a MetadataProvider");
  }
  return context;
};
