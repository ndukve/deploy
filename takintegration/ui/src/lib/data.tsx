import { createContext, useContext, ReactNode, useMemo } from "react";

import { TAK_Zip } from "@/lib/interfaces";

export interface Data {
  tak_zips: TAK_Zip[];
}

const DataContext = createContext<Data | undefined>(undefined);

export const DataProvider = ({
  children,
  data,
}: {
  children: ReactNode;
  data: Data;
}) => {
  const value = useMemo(() => data, [data.tak_zips]);

  return <DataContext.Provider value={value}>{children}</DataContext.Provider>;
};

export const useData = () => {
  const context = useContext(DataContext);
  if (context === undefined) {
    throw new Error("useData must be used within a DataProvider");
  }
  return context;
};
