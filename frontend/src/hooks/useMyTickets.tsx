import { keepPreviousData, useQuery } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { TicketList } from "@/entities/TicketList";
import { Filter } from "@/entities/Filter";

const ticketClient = new APIClient<TicketList>("/api/my-tickets");

const useMyTickets = (accessToken: string, filter?: Filter) => {
  return useQuery<TicketList>({
    queryKey: ["mytickets", filter],
    queryFn: () => ticketClient.getAllFiltered(filter || {}, accessToken),
    retry: 2,
    placeholderData: keepPreviousData,
  });
};

export default useMyTickets;
