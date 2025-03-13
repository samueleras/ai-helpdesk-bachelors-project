import PaginationBar from "@/components/PaginationBar";
import TicketListContainer from "@/components/TicketListContainer";
import useFilteredTickets from "@/hooks/useFilteredTickets";
import { Box } from "@chakra-ui/react";
import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import useAuthStore from "../stores/AuthStore";
import TicketFilter from "@/components/TicketFilter";
import useFilterStore from "@/stores/FilterStore";

const TechnicianPortalPage = () => {
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const pageSize = 10;
  const { ticketFilter } = useFilterStore();

  useEffect(() => {
    if (user?.group !== "technicians") {
      console.log("Access restricted!");
      navigate(-1); //return to previous page
    }
  }, [user]);

  const {
    data: ticketList,
    error,
    refetch,
  } = useFilteredTickets(accessToken, {
    page: page,
    page_size: pageSize,
    ...ticketFilter,
  });

  const location = useLocation();

  useEffect(() => {
    refetch(); // refetch when navigating back to the page
  }, [location.pathname]);

  return (
    <>
      {error && "Error"}
      <Box minH={`calc(100vh - 4rem)`} p={{ base: "1rem", sm: "2rem" }}>
        <TicketFilter />
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

export default TechnicianPortalPage;
