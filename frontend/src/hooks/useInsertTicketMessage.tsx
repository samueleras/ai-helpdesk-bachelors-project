import { useMutation } from "@tanstack/react-query";
import APIClient from "../services/apiClient";
import { NewTicketMessage } from "@/entities/NewTicketMessage";

const ticketMessageClient = new APIClient<void>("/api/insert-ticket-message");

const useInsertTicketMessage = () => {
  return useMutation<
    void,
    Error,
    {
      newTicketMessage: NewTicketMessage;
      accessToken: string;
    }
  >({
    mutationFn: ({ newTicketMessage, accessToken }) =>
      ticketMessageClient.mutate(accessToken, {}, newTicketMessage),
  });
};

export default useInsertTicketMessage;
