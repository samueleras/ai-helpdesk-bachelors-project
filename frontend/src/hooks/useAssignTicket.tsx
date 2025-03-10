import { useMutation } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { TicketAssignee } from "@/entities/TicketAssignee";

const assignTicketClient = new APIClient<void>("/api/assign-ticket");

const useAssignTicket = () => {
  return useMutation<
    void,
    Error,
    {
      ticketAssignee: TicketAssignee;
      accessToken: string;
    }
  >({
    mutationFn: ({ ticketAssignee, accessToken }) =>
      assignTicketClient.mutate(accessToken, {}, ticketAssignee),
  });
};

export default useAssignTicket;
