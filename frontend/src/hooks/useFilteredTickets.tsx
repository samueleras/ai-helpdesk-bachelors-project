import { keepPreviousData, useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { TicketList } from "@/entities/TicketList";
import { TicketFilter } from "@/entities/Filter";

const ticketClient = new APIClient<TicketList>("/api/tickets");

const useFilteredTickets = (accessToken: string, filter?: TicketFilter) => {
  return useQuery<TicketList>({
    queryKey: ["tickets", filter],
    queryFn: () => ticketClient.getAllFiltered(filter || {}, accessToken),
    retry: 2,
    placeholderData: keepPreviousData,
  });
};

export default useFilteredTickets;
