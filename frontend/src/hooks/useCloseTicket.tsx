import { useMutation } from "@tanstack/react-query";
import APIClient from "../services/apiClient";

const ticketCloseClient = new APIClient<void>("/api/close-ticket");

const useCloseTicket = () => {
  return useMutation<
    void,
    Error,
    {
      ticket_id: number;
      accessToken: string;
    }
  >({
    mutationFn: ({ ticket_id, accessToken }) =>
      ticketCloseClient.mutate(accessToken, {}, { ticket_id }),
  });
};

export default useCloseTicket;
