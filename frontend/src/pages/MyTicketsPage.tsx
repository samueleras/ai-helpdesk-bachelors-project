import PaginationBar from "@/components/PaginationBar";
import useMyTickets from "@/hooks/useMyTickets";
import useAuthStore from "@/stores/AuthStore";
import { Spinner, Text } from "@chakra-ui/react";
import { useState } from "react";

const MyTicketsPage = () => {
  const { accessToken } = useAuthStore();
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const {
    data: ticketList,
    error,
    isFetching,
  } = useMyTickets(accessToken, { page: page, page_size: pageSize });

  return (
    <div>
      <h1>MyTicketsPage</h1>
      {error && "Error"}
      {isFetching && <Spinner />}
      {ticketList?.tickets?.map((ticket) => (
        <Text key={ticket.ticket_id}>{ticket.title}</Text>
      ))}
      <PaginationBar
        count={ticketList?.count || 1}
        pageSize={pageSize}
        changePage={setPage}
      />
    </div>
  );
};

export default MyTicketsPage;
