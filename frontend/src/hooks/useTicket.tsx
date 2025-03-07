import { useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { Ticket } from "@/entities/Ticket";

const ticketClient = new APIClient<Ticket>("/api/ticket");

const useTicket = (id: string, accessToken: string) => {
  return useQuery<Ticket>({
    queryKey: ["ticket", id],
    queryFn: () => ticketClient.getByID(id, accessToken),
    refetchInterval: 5000,
    retry: 2,
    staleTime: 1000,
    gcTime: 0,
  });
};

export default useTicket;
