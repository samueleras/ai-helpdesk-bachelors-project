import { Badge, Button, HStack, VStack, Text, Flex } from "@chakra-ui/react";
import { FaHashtag, FaTools, FaUser } from "react-icons/fa";
import { MdDateRange } from "react-icons/md";
import { AssignDropdown } from "./AssignDropdown";
import { IoLockClosed } from "react-icons/io5";
import { Ticket } from "@/entities/Ticket";
import { dateToString } from "@/services/dateToString";
import useCloseTicket from "@/hooks/useCloseTicket";
import useAuthStore from "@/stores/AuthStore";
import useReopenTicket from "@/hooks/useReopenTicket";
import { useEffect, useState } from "react";
import { Toaster, toaster } from "@/components/ui/toaster";

interface TicketDetailsProp {
  ticket: Ticket;
}

const TicketDetails = ({ ticket }: TicketDetailsProp) => {
  const { mutate: closeTicket, error: closeTicketError } = useCloseTicket();
  const { mutate: reopenTicket, error: reopenTicketError } = useReopenTicket();
  const { accessToken, user } = useAuthStore();
  const [closedDate, setClosedDate] = useState(ticket.closed_date);

  useEffect(() => {
    closeTicketError &&
      toaster.create({
        title: "Error",
        description: "Failed to close Ticket. Please try again.",
      });
    setClosedDate(ticket.closed_date);
  }, [closeTicketError]);

  useEffect(() => {
    reopenTicketError &&
      toaster.create({
        title: "Error",
        description: "Failed to reopen Ticket. Please try again.",
      });
    setClosedDate(ticket.closed_date);
  }, [reopenTicketError]);

  const handleCloseTicket = () => {
    closeTicket({ ticket_id: ticket.ticket_id, accessToken });
    setClosedDate(new Date());
  };

  const handleReopenTicket = () => {
    reopenTicket({ ticket_id: ticket.ticket_id, accessToken });
    setClosedDate(undefined);
  };

  return (
    <VStack alignItems={"start"} fontSize={"sm"} gap="3">
      <Toaster />
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
        {user.group === "technicians" ? (
          <AssignDropdown ticket={ticket} />
        ) : (
          <Badge>{ticket.assignee_name || "Unassigned"}</Badge>
        )}
      </HStack>
      <Flex alignItems={"center"} gap=".5rem" flexWrap={"wrap"}>
        <IoLockClosed />
        <Text>Closed:</Text>
        <Badge>{closedDate ? dateToString(closedDate) : "No"}</Badge>
        {user.group === "technicians" &&
          (!closedDate ? (
            <Button onClick={handleCloseTicket} h="1.3rem">
              Close Ticket
            </Button>
          ) : (
            <Button onClick={handleReopenTicket} h="1.3rem">
              Reopen Ticket
            </Button>
          ))}
      </Flex>
    </VStack>
  );
};

export default TicketDetails;
