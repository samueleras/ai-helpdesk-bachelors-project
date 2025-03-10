import { Ticket } from "@/entities/Ticket";
import { Card, Flex, Image } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";
import ticketImage from "../assets/ticket_image.webp";
import TicketDetails from "./TicketDetails";

interface TicketListItemProps {
  ticket: Ticket;
}

export const TicketListItem = ({ ticket }: TicketListItemProps) => {
  const navigate = useNavigate();

  return (
    <Card.Root
      flexDirection="row"
      overflow="hidden"
      border="1px solid darkgray"
    >
      <Image
        display={{ base: "none", md: "block" }}
        objectFit="cover"
        maxW="35%"
        maxH={{ base: "450px", md: "350px" }}
        src={ticketImage}
        alt="Ticket Dummy Image"
        onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
        cursor={"pointer"}
      />
      <Flex>
        <Card.Body>
          <Card.Title
            mb="2"
            onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
            cursor={"pointer"}
          >
            {ticket.title.replace(/"/g, "")}
          </Card.Title>
          <Card.Description
            onClick={() => navigate(`/ticket/${ticket.ticket_id}`)}
            cursor={"pointer"}
            mb="4"
          >
            {ticket.content
              .substring(0, ticket.content.indexOf(".") + 1)
              .replace(/"/g, "")}
          </Card.Description>
          <TicketDetails ticket={ticket} />
        </Card.Body>
      </Flex>
    </Card.Root>
  );
};
