import useMyTickets from "@/hooks/useMyTickets";
import useAuthStore from "@/stores/AuthStore";
import { Spinner, Text } from "@chakra-ui/react";

const MyTicketsPage = () => {
  const { accessToken } = useAuthStore();
  const {
    data: tickets,
    error,
    isFetching,
  } = useMyTickets(accessToken, { page: 1, page_size: 10 });

  return (
    <div>
      <h1>MyTicketsPage</h1>
      {error && "Error"}
      {isFetching && <Spinner />}
      {tickets?.map((ticket) => (
        <Text key={ticket.ticket_id}>{ticket.title}</Text>
      ))}
    </div>
  );
};

export default MyTicketsPage;
