import PaginationBar from "@/components/PaginationBar";
import TicketListContainer from "@/components/TicketListContainer";
import useMyTickets from "@/hooks/useMyTickets";
import useAuthStore from "@/stores/AuthStore";
import { Box, Spinner } from "@chakra-ui/react";
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
    <>
      {error && "Error"}
      {isFetching && <Spinner />}
      <Box minH={`calc(100vh - 4rem)`}>
        <TicketListContainer ticketList={ticketList} />
        <PaginationBar
          count={ticketList?.count || 1}
          pageSize={pageSize}
          changePage={setPage}
        />
      </Box>
    </>
  );
};

export default MyTicketsPage;
