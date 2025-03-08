import { Grid } from "@chakra-ui/react";
import { TicketListItem } from "./TicketListItem";
import { TicketList } from "@/entities/TicketList";

interface TicketListProps {
  ticketList?: TicketList;
}

const TicketListContainer = ({ ticketList }: TicketListProps) => {
  return (
    <Grid
      gridTemplateColumns={{ base: "1fr", xl: "1fr 1fr" }}
      p={{ base: "1rem", sm: "2rem" }}
      gap="2rem"
      mb="3rem"
    >
      {ticketList?.tickets?.map((ticket) => (
        <TicketListItem key={ticket.ticket_id} ticket={ticket} />
      ))}
    </Grid>
  );
};

export default TicketListContainer;
