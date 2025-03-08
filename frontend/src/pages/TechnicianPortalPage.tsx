import { useEffect, useState } from "react";
import useAuthStore from "../stores/AuthStore";
import { useNavigate } from "react-router-dom";
import { Spinner, Text } from "@chakra-ui/react";
import useFilteredTickets from "@/hooks/useFilteredTickets";
import PaginationBar from "@/components/PaginationBar";

const TechnicianPortalPage = () => {
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();
  const [page, setPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    if (user?.group !== "technicians") {
      console.log("Access restricted!");
      navigate(-1); //return to previous page
    }
  }, [user]);

  const {
    data: ticketList,
    error,
    isFetching,
  } = useFilteredTickets(accessToken, { page: page, page_size: pageSize });

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

export default TechnicianPortalPage;
