import { useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { Technician } from "@/entities/Technician";

const techniciansClient = new APIClient<Technician[]>("/api/technicians");

const useTechnicians = (accessToken: string) => {
  return useQuery<Technician[]>({
    queryKey: ["assignee"],
    queryFn: () => techniciansClient.getAll(accessToken),
    retry: 2,
    staleTime: 2 * 60 * 1000,
  });
};

export default useTechnicians;
