import PaginationBar from "@/components/PaginationBar";
import TicketListContainer from "@/components/TicketListContainer";
import useFilteredTickets from "@/hooks/useFilteredTickets";
import { Box } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import TicketFilter from "@/components/TicketFilter";
import useFilterStore from "@/stores/FilterStore";
import { Toaster, toaster } from "@/components/ui/toaster";

const TechnicianPortalPage = () => {
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const { ticketFilter } = useFilterStore();

  useEffect(() => {
    if (user?.group !== "technicians") {
      console.log("Access restricted!");
      navigate("/");
    }
  }, [user]);

  const {
    data: ticketList,
    error: ticketsError,
    refetch,
  } = useFilteredTickets(accessToken, {
    page: page,
    page_size: pageSize,
    ...ticketFilter,
  });

  useEffect(() => {
    if (ticketsError) {
      toaster.create({
        title: "Error",
        type: "error",
        description: "Failed to load tickets. Please try again later.",
      });
    }
  }, [ticketsError]);

  const location = useLocation();

  useEffect(() => {
    refetch(); // refetch when navigating back to the page
  }, [location.pathname]);

  return (
    <>
      <Box minH={`calc(100vh - 4rem)`} p={{ base: "1rem", sm: "2rem" }}>
        <TicketFilter />
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

export default TechnicianPortalPage;
