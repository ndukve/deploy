import { useQuery } from "@tanstack/react-query";
import { API_ENDPOINTS } from "@/lib/api";
import { Credentials } from "@/model/stream-config";

export function useCredentials() {
  return useQuery<Credentials>({
    queryKey: ["credentials"],
    queryFn: async () => {
      const resp = await fetch(API_ENDPOINTS.CREDENTIALS);
      if (!resp.ok) throw new Error("Fetching credentials failed");
      return resp.json() as Promise<Credentials>;
    },
  });
}
