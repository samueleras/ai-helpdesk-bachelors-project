import { keepPreviousData, useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { Ticket } from "@/entities/Ticket";
import { TicketFilter } from "@/entities/Filter";

const ticketClient = new APIClient<Ticket>("/api/tickets");

const useFilteredTickets = (accessToken: string, filter?: TicketFilter) => {
  return useQuery<Ticket[]>({
    queryKey: ["tickets", filter],
    queryFn: () => ticketClient.getAllFiltered(filter || {}, accessToken),
    retry: 2,
    staleTime: 2 * 60 * 1000,
    placeholderData: keepPreviousData,
  });
};

export default useFilteredTickets;
