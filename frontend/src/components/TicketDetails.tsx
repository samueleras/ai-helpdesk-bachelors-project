import { Badge, Button, HStack, VStack, Text } from "@chakra-ui/react";
import { FaHashtag, FaTools, FaUser } from "react-icons/fa";
import { MdDateRange } from "react-icons/md";
import { AssignDropdown } from "./AssignDropdown";
import { IoLockClosed } from "react-icons/io5";
import { Ticket } from "@/entities/Ticket";
import { dateToString } from "@/services/dateToString";
import useCloseTicket from "@/hooks/useCloseTicket";
import useAuthStore from "@/stores/AuthStore";
import useReopenTicket from "@/hooks/useReopenTicket";

interface TicketDetailsProp {
  ticket: Ticket;
}

const TicketDetails = ({ ticket }: TicketDetailsProp) => {
  const { mutate: closeTicket } = useCloseTicket();
  const { mutate: reopenTicket } = useReopenTicket();
  const { accessToken } = useAuthStore();

  const handleCloseTicket = () => {
    closeTicket({ ticket_id: ticket.ticket_id, accessToken });
    ticket.closed_date = new Date();
  };

  const handleReopenTicket = () => {
    reopenTicket({ ticket_id: ticket.ticket_id, accessToken });
    ticket.closed_date = undefined;
  };

  return (
    <VStack alignItems={"start"} fontSize={"sm"} gap="3">
      <HStack>
        <FaUser />
        <Text>Author:</Text>
        <Badge>{ticket.author_name}</Badge>
      </HStack>
      <HStack>
        <FaHashtag />
        <Text>Ticket ID:</Text>
        <Badge>{ticket.ticket_id}</Badge>
      </HStack>
      <HStack>
        <MdDateRange />
        <Text>Creation Date:</Text>
        <Badge>{dateToString(ticket.creation_date)}</Badge>
      </HStack>
      <HStack>
        <FaTools />
        <Text>Assignee:</Text>
        <AssignDropdown />
      </HStack>
      <HStack>
        <IoLockClosed />
        <Text>Closed:</Text>
        <Badge>
          {ticket.closed_date ? dateToString(ticket.closed_date) : "No"}
        </Badge>
        {!ticket.closed_date ? (
          <Button onClick={handleCloseTicket} h="1.3rem">
            Close Ticket
          </Button>
        ) : (
          <Button onClick={handleReopenTicket} h="1.3rem">
            Reopen Ticket
          </Button>
        )}
      </HStack>
    </VStack>
  );
};

export default TicketDetails;
