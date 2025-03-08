import { keepPreviousData, useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { Ticket } from "@/entities/Ticket";
import { Filter } from "@/entities/Filter";

const ticketClient = new APIClient<Ticket>("/api/tickets");

const useMyTickets = (accessToken: string, filter?: Filter) => {
  return useQuery<Ticket[]>({
    queryKey: ["tickets", filter],
    queryFn: () => ticketClient.getAllFiltered(filter || {}, accessToken),
    retry: 2,
    staleTime: 2 * 60 * 1000,
    placeholderData: keepPreviousData,
  });
};

export default useMyTickets;
