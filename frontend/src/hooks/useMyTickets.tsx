import { keepPreviousData, useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { TicketList } from "@/entities/TicketList";
import { Filter } from "@/entities/Filter";

const ticketClient = new APIClient<TicketList>("/api/tickets");

const useMyTickets = (accessToken: string, filter?: Filter) => {
  return useQuery<TicketList>({
    queryKey: ["tickets", filter],
    queryFn: () => ticketClient.getAllFiltered(filter || {}, accessToken),
    retry: 2,
    staleTime: 2 * 60 * 1000,
    placeholderData: keepPreviousData,
  });
};

export default useMyTickets;
