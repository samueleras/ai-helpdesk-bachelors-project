import PaginationBar from "@/components/PaginationBar";
import TicketListContainer from "@/components/TicketListContainer";
import useMyTickets from "@/hooks/useMyTickets";
import useAuthStore from "@/stores/AuthStore";
import { Box } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { Toaster, toaster } from "@/components/ui/toaster";

const MyTicketsPage = () => {
  const { accessToken } = useAuthStore();
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const {
    data: ticketList,
    error: ticketsError,
    refetch,
  } = useMyTickets(accessToken, { page: page, page_size: pageSize });

  const location = useLocation();

  useEffect(() => {
    refetch(); // refetch when navigating back to the page
  }, [location.pathname]);

  useEffect(() => {
    if (ticketsError) {
      toaster.create({
        title: "Error",
        type: "error",
        description: "Failed to load tickets. Please try again later.",
      });
    }
  }, [ticketsError]);

  return (
    <>
      <Box minH={`calc(100vh - 4rem)`} p={{ base: "1rem", sm: "2rem" }}>
        <TicketListContainer ticketList={ticketList} />
      </Box>
      <PaginationBar
        count={ticketList?.count || 1}
        pageSize={pageSize}
        changePage={setPage}
      />
      <Toaster />
    </>
  );
};

export default MyTicketsPage;
