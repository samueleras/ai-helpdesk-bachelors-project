import { useEffect } from "react";
import useAuthStore from "../stores/AuthStore";
import { useNavigate } from "react-router-dom";
import { Spinner, Text } from "@chakra-ui/react";
import useFilteredTickets from "@/hooks/useFilteredTickets";

const TechnicianPortalPage = () => {
  const { user, accessToken } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    if (user?.group !== "technicians") {
      console.log("Access restricted!");
      navigate(-1); //return to previous page
    }
  }, [user]);

  const {
    data: tickets,
    error,
    isFetching,
  } = useFilteredTickets(accessToken, { page: 1, page_size: 10 });

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

export default TechnicianPortalPage;
