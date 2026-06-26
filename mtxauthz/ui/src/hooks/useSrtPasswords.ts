import { useQuery } from "@tanstack/react-query";
import { API_ENDPOINTS } from "@/lib/api";
import { SrtPasswords } from "@/model/stream-config";

export function useSrtPasswords() {
  return useQuery<SrtPasswords>({
    queryKey: ["srt_default"],
    queryFn: async () => {
      const resp = await fetch(API_ENDPOINTS.SRT_DEFAULT);
      if (!resp.ok) throw new Error("Fetching SRT passwords failed");
      return resp.json() as Promise<SrtPasswords>;
    },
  });
}
