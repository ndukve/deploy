import { useQuery } from "@tanstack/react-query";
import { StreamConfig } from "@/model/stream-config";
import { API_ENDPOINTS } from "@/lib/api";

export function useStreams() {
  return useQuery<StreamConfig[]>({
    queryKey: ["streams"],
    queryFn: async () => {
      const resp = await fetch(API_ENDPOINTS.STREAMS);
      if (!resp.ok) throw new Error("Fetching streams failed");
      return resp.json() as Promise<StreamConfig[]>;
    },
    refetchInterval: 15_000,
  });
}
