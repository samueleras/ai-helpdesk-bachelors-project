import { useMutation } from "@tanstack/react-query";
import APIClient from "../services/apiClient";

const ticketReopenClient = new APIClient<void>("/api/reopen-ticket");

const useReopenTicket = () => {
  return useMutation<
    void,
    Error,
    {
      ticket_id: number;
      accessToken: string;
    }
  >({
    mutationFn: ({ ticket_id, accessToken }) =>
      ticketReopenClient.mutate(accessToken, {}, { ticket_id }),
  });
};

export default useReopenTicket;
